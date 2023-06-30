import os
import json
from pathlib import Path
import argparse
import random
import string
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    Environment,
    CodeConfiguration,
)
from azure.identity import DefaultAzureCredential
from azure.ai.ml.constants import AssetTypes

# arguments expected for executing the experiments
parser = argparse.ArgumentParser("provision_endpoints")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--endpoint_name", type=str, help="Azureml realtime endpoint name")
parser.add_argument("--is_local", type=str, help="local endpoint provisioning")
args = parser.parse_args()


endpoint_name = args.endpoint_name
local = args.is_local

print(f"Endpoint name: {endpoint_name}")

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name
)

endpoint = ManagedOnlineEndpoint(
    name=endpoint_name,
    description="An online endpoint serving an MLflow model for the diabetes classification task",
    auth_mode="key",
    tags={"foo": "bar"},
)
if local == "False":
    ml_client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()
