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
from azure.ai.ml.entities import (
    BatchEndpoint,
    ModelBatchDeployment,
    ModelBatchDeploymentSettings,
    Data,
    BatchRetrySettings
)
from azure.ai.ml.constants import AssetTypes, BatchDeploymentOutputAction

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
parser.add_argument("--batch_config", type=str, help="file path to batch config")
parser.add_argument("--env_type", type=str, help="env name (dev, test, prod) for deployment")

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
batch_config = args.batch_config
env_type = args.env_type

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

if batch == "False":
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

else:
    batch_file = open(batch_config)
    batch_data = json.load(batch_file)

    for elem in batch_data['models']:
        if 'ENV_NAME' in elem:
            if env_type == elem["ENV_NAME"]:
                batch_cluster_name = elem["BATCH_CLUSTER_NAME"]
                cluster_instance_count = elem["CLUSTER_INSTANCE_COUNT"]
                max_concurrency_per_instance = elem["MAX_CONCURRENCY_PER_INSTANCE"]
                mini_batch_size = elem["MINI_BATCH_SIZE"]
                output_file_name = elem["OUTPUT_FILE_NAME"]
                max_retries = elem["MAX_RETRIES"]
                retry_timeout = elem["RETRY_TIMEOUT"]

                deployment = ModelBatchDeployment(
                    name=deployment_name,
                    description="A heart condition classifier based on XGBoost",
                    endpoint_name=endpoint_name,
                    model=model,
                    compute=batch_cluster_name,
                    settings=ModelBatchDeploymentSettings(
                        instance_count=cluster_instance_count,
                        max_concurrency_per_instance=max_concurrency_per_instance,
                        mini_batch_size=mini_batch_size,
                        output_action=BatchDeploymentOutputAction.APPEND_ROW,
                        output_file_name=output_file_name,
                        retry_settings=BatchRetrySettings(max_retries=max_retries, timeout=retry_timeout),
                        logging_level="info",
                    ),
                    tags={"build_id": build_id, "run_id": run_id}
                )

                ml_client.batch_deployments.begin_create_or_update(deployment).result()

                endpoint = ml_client.batch_endpoints.get(endpoint_name)
                endpoint.defaults.deployment_name = deployment_name
                ml_client.batch_endpoints.begin_create_or_update(endpoint).result()

