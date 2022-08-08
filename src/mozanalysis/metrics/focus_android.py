# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# These metric definitions are deprected.
# Instead use the metric slug to reference metrics defined
# in https://github.com/mozilla/jetstream-config

from mozanalysis.config import ConfigLoader

baseline = ConfigLoader.get_data_source("baseline", "focus_android")

events = ConfigLoader.get_data_source("events", "focus_android")

metrics = ConfigLoader.get_data_source("metrics", "focus_android")

baseline_ping_count = ConfigLoader.get_metric("baseline_ping_count", "focus_android")

metric_ping_count = ConfigLoader.get_metric("metric_ping_count", "focus_android")

first_run_date = ConfigLoader.get_metric("first_run_date", "focus_android")
