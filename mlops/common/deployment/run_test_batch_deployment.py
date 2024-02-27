"""This module provides functionalities for testing a machine learning model deployed on Azure."""
import argparse

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, Input
from azure.ai.ml.constants import AssetTypes

from mlops.common.config_utils import MLOpsConfig


def main():
    """Test a deployed model."""
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

    deployment_config = config.get_deployment_config(deployment_name=f"{model_type}_batch")

    dataset_unlabeled = ml_client.data.get(
        name=deployment_config["test_dataset_name"], label="latest"
    )

    input = Input(type=AssetTypes.URI_FOLDER, path=dataset_unlabeled.id)

    job = ml_client.batch_endpoints.invoke(
        deployment_name=deployment_config["deployment_name"],
        endpoint_name=deployment_config["endpoint_name"],
        input=input,
    )

    ml_client.jobs.stream(job.name)

    scoring_job = list(ml_client.jobs.list(parent_job_name=job.name))[0]

    print("Job name:", scoring_job.name)
    print("Job status:", scoring_job.status)
    print(
        "Job duration:",
        scoring_job.creation_context.last_modified_at
        - scoring_job.creation_context.created_at,
    )

    ml_client.jobs.download(name=scoring_job.name, download_path=".", output_name="score")


if __name__ == "__main__":
    main()
