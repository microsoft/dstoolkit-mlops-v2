import argparse
import os
import json
from azure.ai.ml import MLClient

from azure.identity import DefaultAzureCredential

parser = argparse.ArgumentParser("test_model")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--endpoint_name", type=str, help="AML endpoint name")
parser.add_argument("--deployment_name", type=str, help="AML deployment name")
parser.add_argument("--test_model_file", type=str, help="Test model file")
args = parser.parse_args()

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id,  args.resource_group_name,  args.workspace_name
)

endpoint_name = args.endpoint_name
deployment_name = args.deployment_name
test_model_file = args.test_model_file

endpoint_url = ml_client.online_endpoints.get(name=endpoint_name).scoring_uri
api_key = ml_client.online_endpoints.get_keys(name=endpoint_name).primary_key

request_result = ml_client.online_endpoints.invoke(
    endpoint_name=endpoint_name,
    deployment_name=deployment_name,
    request_file=test_model_file,
)

print(request_result)