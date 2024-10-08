#!/bin/bash
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


if [ $# != 5 ]; then
    echo "Usage: $0 gcp_project_id bucket_name region service_account_email share_crash_usage_stats(true/false)"
    echo "Sharing crash/usage stats helps us suporting the solution (E.g. true/false)"
    exit 1
fi

echo "Move to megalista_dataflow folder"
cd megalista_dataflow
echo "Configuration GCP project in gcloud"
gcloud config set project "$1"
echo "Upgrading pip to latest version"
python3 -m pip install --upgrade pip
echo "Build Dataflow metadata"
# python3 -m pip install --user -q -r requirements.txt
python3 -m pip install -r requirements.txt
echo $4
echo "Update commit info inside code"
sed -i "s/MEGALISTA_VERSION\s*=.*/MEGALISTA_VERSION = '$(git rev-parse HEAD)'/" ./config/version.py
python3 -m main \
    --runner DataflowRunner \
    --project "$1" \
    --gcp_project_id "$1" \
    --temp_location "gs://$2/tmp/" \
    --region "$3" \
    --setup_file ./setup.py \
    --template_location "gs://$2/templates/megalista" \
    --num_workers 1 \
    --autoscaling_algorithm=NONE \
    --service_account_email "$4" \
    --collect_usage_stats "$5"
echo "Copy megalista_medata to bucket $2"
gsutil cp megalista_metadata "gs://$2/templates/megalista_metadata"
echo "Cleanup"
sed -i "s/MEGALISTA_VERSION\s*=.*/MEGALISTA_VERSION = '\[megalista_version\]'/" ./config/version.py
cd ..
echo "Finished"
