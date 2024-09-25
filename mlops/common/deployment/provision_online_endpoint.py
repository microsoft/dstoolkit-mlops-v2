"""
This module is designed for provisioning Azure Machine Learning endpoints.

It utilizes the Azure ML SDK (MLClient) to create or update managed online and batch endpoints in an Azure ML workspace.
"""
import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineEndpoint
from azure.identity import DefaultAzureCredential
from mlops.common.config_utils import MLOpsConfig


def main():
    """Create Azure ML endpoint."""
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

    endpoint = ManagedOnlineEndpoint(
        name=deployment_config["endpoint_name"],
        description=deployment_config["endpoint_desc"],
        auth_mode="key",
        tags={
            "build_id": config.environment_configuration["build_reference"],
            "run_id": run_id,
        },
    )

    ml_client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()


if __name__ == "__main__":
    main()
