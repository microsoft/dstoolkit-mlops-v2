import os
import json
from pathlib import Path
import argparse
import random
import string
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint
)
from azure.identity import DefaultAzureCredential
from azure.ai.ml.constants import AssetTypes

# arguments expected for executing the experiments
parser = argparse.ArgumentParser("provision_endpoints")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--endpoint_name", type=str, help="Azureml realtime endpoint name")
parser.add_argument("--build_id", type=str, help="build responsbile for deployment")
parser.add_argument("--is_batch", type=str, help="batch endpoint provisioning")
args = parser.parse_args()


endpoint_name = args.endpoint_name
batch = args.is_batch
build_id = args.build_id

print(f"Endpoint name: {endpoint_name}")

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name
)

if batch == "False":
    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name,
        description="An online endpoint serving an MLflow model for the diabetes classification task",
        auth_mode="key",
        tags={"build_id": build_id},
    )

    ml_client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()
