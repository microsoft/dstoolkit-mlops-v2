"""
This script automates the deployment of machine learning models in Azure Machine Learning.

It supports both batch and real-time deployment scenarios, determining the type based on the
provided arguments. The script reads configuration details from specified JSON files and uses
these to set up and configure the model deployments.

It also handles various deployment settings such as endpoint names, deployment names, environment
variables, and computing resources. The script is intended to be run with command-line arguments
specifying Azure subscription details, model information, and deployment preferences.
"""
import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import (
    ModelBatchDeployment,
    ModelBatchDeploymentSettings,
    BatchRetrySettings,
)
from azure.ai.ml.constants import BatchDeploymentOutputAction
from mlops.common.config_utils import MLOpsConfig
from mlops.common.naming_utils import generate_model_name


parser = argparse.ArgumentParser("provision_deployment")
parser.add_argument(
    "--model_type", type=str, help="registered model type to be deployed", required=True
)
parser.add_argument(
    "--environment_name",
    type=str,
    help="env name (dev, test, prod) for deployment",
    required=True,
)
parser.add_argument(
    "--run_id", type=str, help="AML run id for model generation", required=True
)
args = parser.parse_args()

model_type = args.model_type
run_id = args.run_id
env_type = args.environment_name

config = MLOpsConfig(environment=env_type)

ml_client = MLClient(
    DefaultAzureCredential(),
    config.aml_config["subscription_id"],
    config.aml_config["resource_group_name"],
    config.aml_config["workspace_name"],
)

deployment_config = config.get_deployment_config(deployment_name=f"{model_type}_batch")

published_model_name = generate_model_name(model_type)

model_refs = ml_client.models.list(published_model_name)
latest_version = max(model.version for model in model_refs)
model = ml_client.models.get(published_model_name, latest_version)

environment = Environment(
    name="prs-env",
    conda_file=deployment_config["conda_file"],
    image=deployment_config["deployment_base_image"],
)

deployment = ModelBatchDeployment(
    name=deployment_config["deployment_name"],
    description="model with batch endpoint",
    endpoint_name=deployment_config["endpoint_name"],
    model=model,
    environment=environment,
    compute=deployment_config["batch_cluster_name"],
    settings=ModelBatchDeploymentSettings(
        instance_count=deployment_config["cluster_instance_count"],
        max_concurrency_per_instance=deployment_config["max_concurrency_per_instance"],
        mini_batch_size=deployment_config["mini_batch_size"],
        output_action=BatchDeploymentOutputAction.APPEND_ROW,
        output_file_name=deployment_config["output_file_name"],
        retry_settings=BatchRetrySettings(
            max_retries=deployment_config["max_retries"],
            timeout=deployment_config["retry_timeout"],
        ),
        logging_level="info",
    ),
    tags={
        "build_id": config.environment_configuration["build_reference"],
        "run_id": run_id,
    },
)

ml_client.batch_deployments.begin_create_or_update(deployment).result()

endpoint = ml_client.batch_endpoints.get(deployment_config["endpoint_name"])
endpoint.defaults.deployment_name = deployment.name
ml_client.batch_endpoints.begin_create_or_update(endpoint).result()
print(f"The default deployment is {endpoint.defaults.deployment_name}")
