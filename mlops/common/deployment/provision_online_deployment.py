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
from azure.ai.ml.entities import (
    ManagedOnlineDeployment,
    Environment,
    CodeConfiguration,
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
    description=deployment_desc,
    environment=environment,
    code_configuration=CodeConfiguration(
        code=score_dir, scoring_script=score_file_name
    ),
    instance_type=deployment_vm_size,
    instance_count=deployment_instance_count,
    environment_variables=dict(environment_variables),
    tags={"build_id": build_id, "run_id": run_id},
)

ml_client.online_deployments.begin_create_or_update(blue_deployment).result()
