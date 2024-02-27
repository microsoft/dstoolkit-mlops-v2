"""This module provides functionality for testing a machine learning model deployed."""
import argparse
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from mlops.common.config_utils import MLOpsConfig


def main():
    """Test a deployed model."""
    parser = argparse.ArgumentParser("test_nodel")
    parser.add_argument(
        "--model_type", type=str, help="registered model type to be deployed", required=True
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        help="env name (dev, test, prod) for deployment",
        required=True,
    )
    args = parser.parse_args()

    model_type = args.model_type
    env_type = args.environment_name

    config = MLOpsConfig(environment=env_type)

    ml_client = MLClient(
        DefaultAzureCredential(),
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
    )

    deployment_config = config.get_deployment_config(deployment_name=f"{model_type}_online")

    # endpoint_url = ml_client.online_endpoints.get(
    #     name=deployment_config["endpoint_name"]
    # ).scoring_uri
    # api_key = ml_client.online_endpoints.get_keys(
    #     name=deployment_config["endpoint_name"]
    # ).primary_key

    request_result = ml_client.online_endpoints.invoke(
        endpoint_name=deployment_config["endpoint_name"],
        deployment_name=deployment_config["deployment_name"],
        request_file=deployment_config["test_file_path"],
    )

    print(request_result)


if __name__ == "__main__":
    main()
