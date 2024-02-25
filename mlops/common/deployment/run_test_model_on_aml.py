"""
This module provides functionality for testing a machine learning model deployed.

The script reads deployment configuration from a specified JSON file and determines
the appropriate endpoint and deployment settings based on the provided environment
name (e.g., dev, test, prod). It then uses the Azure Machine Learning client to interact
with the specified deployment, sending a test request to the model endpoint and
displaying the result.
"""

import argparse
import json
from azure.ai.ml import MLClient

from azure.identity import DefaultAzureCredential

parser = argparse.ArgumentParser("test_nodel")
parser.add_argument("--model_type", type=str, help="registered model type to be deployed", required=True)
parser.add_argument("--env_type", type=str, help="env name (dev, test, prod) for deployment", required=True)
parser.add_argument("--run_id", type=str, help="AML run id for model generation", required=True)
args = parser.parse_args()

model_type = args.model_type
run_id = args.run_id
env_type = args.env_type

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name
)

endpoint_url = ml_client.online_endpoints.get(name=endpoint_name).scoring_uri
api_key = ml_client.online_endpoints.get_keys(name=endpoint_name).primary_key

request_result = ml_client.online_endpoints.invoke(
    endpoint_name=endpoint_name,
    deployment_name=deployment_name,
    request_file=test_model_file,
)

print(request_result)
