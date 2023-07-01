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
parser.add_argument("--deployment_name", type=str, help="Azureml realtime deployment name")
parser.add_argument("--deployment_traffic_allocation", type=str, help="Azureml realtime deployment traffic allocation")
parser.add_argument("--deployment_vm_size", type=str, help="Azureml realtime deployment vm size")
parser.add_argument("--model_name", type=str, help="registered model name to be deployed")
parser.add_argument("--deployment_base_image", type=str, help="Azureml inference image name")
parser.add_argument("--deployment_conda_path", type=str, help="conda file path for inferencing image")
parser.add_argument("--score_dir", type=str, help="name of directory with score file")
parser.add_argument("--score_file_name", type=str, help="score file name")
parser.add_argument("--build_id", type=str, help="build responsbile for deployment")
parser.add_argument("--run_id", type=str, help="run responsbile for model generation")
parser.add_argument("--is_batch", type=str, help="batch deployment")
args = parser.parse_args()

endpoint_name = args.endpoint_name
deployment_name = args.deployment_name
model_name = args.model_name
deployment_vm_size = args.deployment_vm_size
deployment_base_image = args.deployment_base_image
deployment_conda_path = args.deployment_conda_path
score_dir =  args.score_dir
score_file_name = args.score_file_name
build_id = args.build_id
run_id = args.run_id
batch = args.is_batch

print(f"Endpoint name: {endpoint_name}")
print(f"Endpoint name: {deployment_name}")
print(f"Model name: {model_name}")
print(f"score_dir: {score_dir}")
print(f"score_file_name: {score_file_name}")
print(f"deployment_base_image: {deployment_base_image}")
print(f"deployment_conda_path: {deployment_conda_path}")

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name
)

model_refs = ml_client.models.list(model_name)
latest_version = max(model.version for model in model_refs)
model = ml_client.models.get(model_name, latest_version)

environment = Environment(
    conda_file=deployment_conda_path,
    image=deployment_base_image,
)

blue_deployment = ManagedOnlineDeployment(
    name=deployment_name,
    endpoint_name=endpoint_name,
    model=model,
    environment=environment,
    code_configuration=CodeConfiguration(
        code=score_dir, scoring_script=score_file_name
    ),
    instance_type=deployment_vm_size,
    instance_count=1,
    tags={"build_id": build_id, "run_id": run_id},
)

ml_client.online_deployments.begin_create_or_update(blue_deployment).result()

#endpoint.traffic = {blue_deployment.name: 100}
#ml_client.begin_create_or_update(endpoint).result()