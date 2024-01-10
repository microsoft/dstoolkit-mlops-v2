
import json
import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineDeployment,
    Environment,
    CodeConfiguration,
)
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import (
    ModelBatchDeployment,
    ModelBatchDeploymentSettings,
    BatchRetrySettings
)
from azure.ai.ml.constants import BatchDeploymentOutputAction


parser = argparse.ArgumentParser("provision_deployment")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id", required=True)
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group", required=True)
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name", required=True)
parser.add_argument("--model_name", type=str, help="registered model name to be deployed", required=True)
parser.add_argument("--build_id", type=str, help="Azure DevOps build id for deployment", required=True)
parser.add_argument("--run_id", type=str, help="AML run id for model generation", required=True)
parser.add_argument("--is_batch", type=str, help="True for batch endpoint and False for real-time endpoint", required=True)
parser.add_argument("--batch_config", type=str, help="file path of batch config")
parser.add_argument("--env_type", type=str, help="env name (dev, test, prod) for deployment", required=True)
parser.add_argument("--realtime_deployment_config", type=str, help="file path of realtime config")
args = parser.parse_args()


model_name = args.model_name
build_id = args.build_id
run_id = args.run_id
batch = args.is_batch
if args.batch_config is not None:
    batch_config = args.batch_config
if args.realtime_deployment_config is not None:
    real_config = args.realtime_deployment_config
env_type = args.env_type

print(f"Model name: {model_name}")


ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name
)

model_refs = ml_client.models.list(model_name)
latest_version = max(model.version for model in model_refs)
model = ml_client.models.get(model_name, latest_version)

if batch == "False":

    config_file = open(real_config)
    endpoint_config = json.load(config_file)
    for elem in endpoint_config['real_time']:
        if 'ENDPOINT_NAME' in elem and 'ENV_NAME' in elem:
            if env_type == elem['ENV_NAME']:
                endpoint_name = elem["ENDPOINT_NAME"]
                deployment_name = elem["DEPLOYMENT_NAME"]
                deployment_conda_path = elem["DEPLOYMENT_CONDA_PATH"]
                deployment_base_image = elem["DEPLOYMENT_BASE_IMAGE_NAME"]
                score_dir = elem["SCORE_DIR"]
                score_file_name = elem["SCORE_FILE_NAME"]
                deployment_vm_size = elem["DEPLOYMENT_VM_SIZE"]
                deployment_instance_count = elem["DEPLOYMENT_INSTANCE_COUNT"]
                deployment_desc = elem["DEPLOYMENT_DESC"]
                environment_variables = elem["ENVIRONMENT_VARIABLES"]

                
                environment = Environment(
                    conda_file=deployment_conda_path,
                    image=deployment_base_image,
                    user_managed_dependencies = True
                )
                
                blue_deployment = ManagedOnlineDeployment(
                    name=deployment_name,
                    endpoint_name=endpoint_name,
                    model=model,
                    description=deployment_desc,
                    environment=environment,
                    code_configuration=CodeConfiguration(
                        code=score_dir, scoring_script=score_file_name
                    ),
                    instance_type=deployment_vm_size,
                    instance_count=deployment_instance_count,
                    environment_variables = dict(environment_variables),
                    tags={"build_id": build_id, "run_id": run_id},
                )

                ml_client.online_deployments.begin_create_or_update(blue_deployment).result()

else:
    batch_file = open(batch_config)
    batch_data = json.load(batch_file)

    for elem in batch_data['batch_config']:
        if 'ENDPOINT_NAME' in elem and 'ENV_NAME' in elem:
            if env_type == elem["ENV_NAME"]:
                endpoint_name = elem["ENDPOINT_NAME"]
                deployment_name = elem["DEPLOYMENT_NAME"]
                batch_cluster_name = elem["BATCH_CLUSTER_NAME"]
                cluster_instance_count = elem["CLUSTER_INSTANCE_COUNT"]
                max_concurrency_per_instance = elem["MAX_CONCURRENCY_PER_INSTANCE"]
                mini_batch_size = elem["MINI_BATCH_SIZE"]
                output_file_name = elem["OUTPUT_FILE_NAME"]
                max_retries = elem["MAX_RETRIES"]
                retry_timeout = elem["RETRY_TIMEOUT"]
                deployment_conda_path = elem["DEPLOYMENT_CONDA_PATH"]
                deployment_base_image = elem["DEPLOYMENT_BASE_IMAGE_NAME"]

                
                environment = Environment(
                    conda_file=deployment_conda_path,
                    image=deployment_base_image,
                )
                environment.python.user_managed_dependencies = True
                
                deployment = ModelBatchDeployment(
                    name=deployment_name,
                    description="model with batch endpoint",
                    endpoint_name=endpoint_name,
                    model=model,
                    compute=batch_cluster_name,
                    environment=environment,
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

