"""
This module is designed for provisioning Azure Machine Learning endpoints.

It utilizes the Azure ML SDK (MLClient) to create or update managed online and batch endpoints in an Azure ML workspace.
The script is intended to be run as a command-line utility and requires several arguments to specify Azure subscription,
resource group, workspace, and details related to the endpoint configuration.
"""
import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint
)
from azure.identity import DefaultAzureCredential


parser = argparse.ArgumentParser("provision_deployment")
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

endpoint = ManagedOnlineEndpoint(
    name=endpoint_name,
    description=endpoint_desc,
    auth_mode="key",
    tags={"build_id": build_id, "run_id": run_id},
)

ml_client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()
