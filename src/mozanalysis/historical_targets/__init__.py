# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from typing import Optional
import datetime

import attr

@attr.s(frozen=True, slots=True)
class TargetDataSource:
    """Represents a table or view, from which historical data may be defined
    to size experiments.

    Args:
        name (str): Name for the Data Source. Should be unique to avoid
            confusion.
        from_expr (str): FROM expression - often just a fully-qualified
            table name. Sometimes a subquery. May contain the string
            ``{dataset}`` which will be replaced with an app-specific
            dataset for Glean apps. If the expression is templated
            on dataset, default_dataset is mandatory.
        client_id_column (str, optional): Name of the column that
            contains the ``client_id`` (join key). Defaults to
            'client_id'.
        submission_date_column (str, optional): Name of the column
            that contains the submission date (as a date, not
            timestamp). Defaults to 'submission_date'.
        default_dataset (str, optional): The value to use for
            `{dataset}` in from_expr if a value is not provided
            at runtime. Mandatory if from_expr contains a
            `{dataset}` parameter.
    """

    name = attr.ib(validator=attr.validators.instance_of(str))
    _from_expr = attr.ib(validator=attr.validators.instance_of(str))
    client_id_column = attr.ib(default="client_id", type=str)
    submission_date_column = attr.ib(default="submission_date", type=str)
    default_dataset = attr.ib(default=None, type=Optional[str])

    @default_dataset.validator
    def _check_default_dataset_provided_if_needed(self, attribute, value):
        self.from_expr_for(None)

    def from_expr_for(self, dataset: Optional[str]) -> str:
        """Expands the ``from_expr`` template for the given dataset.
        If ``from_expr`` is not a template, returns ``from_expr``.

        Args:
            dataset (str or None): Dataset name to substitute
                into the from expression.
        """
        effective_dataset = dataset or self.default_dataset
        if effective_dataset is None:
            try:
                return self._from_expr.format()
            except Exception as e:
                raise ValueError(
                    f"{self.name}: from_expr contains a dataset template but no value was provided."  # noqa:E501
                ) from e
        return self._from_expr.format(dataset=effective_dataset)

    def build_query(
        self,
        target_list,
        time_limits,
        from_expr_dataset=None,
    ):
        """Return a nearly-self contained SQL query.

        This query returns all distinct client IDs that satisfy the criteria
        for inclusion in the analysis for this datasource. Separate sub-queries
        are constructed for each additional data source in the analysis.
        """
        return """
        SELECT DISTINCT
            ds.{client_id} as client_id
        FROM {from_expr} ds
        WHERE {where_expr}
            AND ds.{submission_date} BETWEEN '{fddr}' AND '{lddr}'
            """.format(
            client_id=self.client_id_column,
            submission_date=self.submission_date_column,
            from_expr=self.from_expr_for(from_expr_dataset),
            fddr=time_limits.first_enrollment_date,
            lddr=time_limits.last_enrollment_date,
            where_expr = " \n AND ".join([target.where_expr for target in target_list]) if len(target_list) > 1
                    else target_list[0].where_expr ,
        )

@attr.s(frozen=True, slots=True)
class Target:
    """Represents a target dataset for historical data.

    Args:
        name (str): The targets's name; will be a column name.
        data_source (SegmentDataSource): Data source that provides
            the columns referenced in ``where_expr``.
        where_expr (str): A SQL WHERE expression that filters the 
            DataSource table to client ids that will satisfy conditions for
            the analysis
        description (str): A paragraph of Markdown-formatted text describing
            the segment in more detail, to be shown on dashboards
    """

    name = attr.ib(type=str)
    data_source = attr.ib(validator=attr.validators.instance_of(TargetDataSource))
    where_expr = attr.ib(type=str)
    friendly_name = attr.ib(type=Optional[str], default=None)
    description = attr.ib(type=Optional[str], default=None)
