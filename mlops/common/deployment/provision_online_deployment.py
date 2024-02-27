"""
This script automates the deployment of machine learning models in Azure Machine Learning.

It supports real-time deployment scenarios.
"""
import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineDeployment,
    Environment,
    CodeConfiguration,
)
from azure.identity import DefaultAzureCredential
from mlops.common.config_utils import MLOpsConfig
from mlops.common.naming_utils import generate_model_name


def main():
    """Automate the deployment of machine learning models in Azure Machine Learning."""
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

    deployment_config = config.get_deployment_config(deployment_name=f"{model_type}_online")

    published_model_name = generate_model_name(model_type)

    model_refs = ml_client.models.list(published_model_name)
    latest_version = max(model.version for model in model_refs)
    model = ml_client.models.get(published_model_name, latest_version)

    environment = Environment(
        conda_file=deployment_config["deployment_conda_path"],
        image=deployment_config["deployment_base_image"],
    )

    blue_deployment = ManagedOnlineDeployment(
        name=deployment_config["deployment_name"],
        endpoint_name=deployment_config["endpoint_name"],
        model=model,
        description=deployment_config["deployment_desc"],
        environment=environment,
        code_configuration=CodeConfiguration(
            code=deployment_config["score_dir"],
            scoring_script=deployment_config["score_file_name"],
        ),
        instance_type=deployment_config["deployment_vm_size"],
        instance_count=deployment_config["deployment_instance_count"],
        tags={
            "build_id": config.environment_configuration["build_reference"],
            "run_id": run_id,
        },
    )

    ml_client.online_deployments.begin_create_or_update(blue_deployment).result()


if __name__ == "__main__":
    main()
