"""
This script allows us to add a special tag in the case if the model has been approved.

Later, we will use this tag to execute CD pipeline and deploy the model into the production
"""
import argparse
import mlflow
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from mlops.common.config_utils import MLOpsConfig
from mlops.common.naming_utils import generate_model_name


def main():
    """Take the latest version of the model and add  ready_for_production tag."""
    parser = argparse.ArgumentParser("provision_deployment")
    parser.add_argument(
        "--model_type", type=str, help="registered model type to be deployed", required=True
    )
    args = parser.parse_args()

    model_type = args.model_type

    config = MLOpsConfig()

    ml_client = MLClient(
        DefaultAzureCredential(),
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
    )

    published_model_name = generate_model_name(model_type)

    azureml_tracking_uri = ml_client.workspaces.get(
        ml_client.workspace_name
    ).mlflow_tracking_uri
    mlflow.set_tracking_uri(azureml_tracking_uri)

    client = mlflow.tracking.MlflowClient()

    # TODO: In general we should not rely on the latest version, and it should be passed to this step
    last_version = client.search_model_versions(filter_string=f"name='{published_model_name}'")[0].version

    client.set_model_version_tag(
        name=published_model_name, version=last_version, key="stage", value="ready_for_production"
    )


if __name__ == "__main__":
    main()
