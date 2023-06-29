import os
import json
from pathlib import Path
import argparse
import random
import string

# arguments expected for executing the experiments
parser = argparse.ArgumentParser("provision_endpoints")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--endpoint_name", type=str, help="Azureml realtime endpoint name")
args = parser.parse_args()

allowed_chars = string.ascii_lowercase + string.digits
endpoint_suffix = "".join(random.choice(allowed_chars) for x in range(5))
endpoint_name = "diabetes-endpoint-" + args.endpoint_name

print(f"Endpoint name: {endpoint_name}")

endpoint = ManagedOnlineEndpoint(
    name=endpoint_name,
    description="An online endpoint serving an MLflow model for the diabetes classification task",
    auth_mode="key",
    tags={"foo": "bar"},
)

ml_client.online_endpoints.begin_create_or_update(endpoint).result()