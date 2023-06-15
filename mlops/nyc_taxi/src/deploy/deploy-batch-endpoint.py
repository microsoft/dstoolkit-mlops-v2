import argparse

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    BatchEndpoint,
    ModelBatchDeployment,
    ModelBatchDeploymentSettings,
    AmlCompute,
    BatchRetrySettings,
)
from azure.ai.ml.constants import BatchDeploymentOutputAction
from azure.identity import DefaultAzureCredential


def main(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    name: str,
    endpoint_name: str,
    model_name: str,
    compute_name: str,
):
    print("Get AML Workspace handler...")
    ml_client = MLClient(
        DefaultAzureCredential(), subscription_id, resource_group_name, workspace_name
    )

    print("Get or create AML compute...")
    if not any(filter(lambda m: m.name == compute_name, ml_client.compute.list())):
        compute_cluster = AmlCompute(
            name=compute_name,
            description="amlcompute",
            min_instances=0,
            max_instances=5,
        )
        ml_client.begin_create_or_update(compute_cluster).result()

    print("Deploy batch endpoint...")
    endpoint = BatchEndpoint(
        name=endpoint_name,
        description="this is a sample online endpoint",
    )

    ml_client.batch_endpoints.begin_create_or_update(endpoint).result()

    print("Deploying to endpoint...")
    deployment = ModelBatchDeployment(
        name=name,
        endpoint_name=endpoint_name,
        model=model_name + "@latest",
        compute=compute_name,
        settings=ModelBatchDeploymentSettings(
            instance_count=2,
            max_concurrency_per_instance=2,
            mini_batch_size=10,
            output_action=BatchDeploymentOutputAction.APPEND_ROW,
            output_file_name="predictions.csv",
            retry_settings=BatchRetrySettings(max_retries=3, timeout=300),
            logging_level="info",
        ),
    )

    ml_client.batch_deployments.begin_create_or_update(deployment).result()

    print("Update default deployment...")
    endpoint = ml_client.batch_endpoints.get(endpoint.name)
    endpoint.defaults.name = deployment.name
    ml_client.batch_endpoints.begin_create_or_update(endpoint).result()


if __name__ == "__main__":
    print('Begin parsing arguments...')
    parser = argparse.ArgumentParser(description="Create online deployment")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )
    parser.add_argument("--deployment_name", type=str, help="Name of online deployment")
    parser.add_argument("--endpoint_name", type=str, help="Name of the online endpoint")
    parser.add_argument("--model_name", type=str, help="AML model name")
    parser.add_argument("--compute_name", type=str, help="AML compute name")

    args = parser.parse_args()

    print('Parsing complete.')

    subscription_id = args.subscription_id
    resource_group_name = args.resource_group_name
    workspace_name = args.workspace_name
    name = args.deployment_name
    endpoint_name = args.endpoint_name
    model_name = args.model_name
    compute_name = args.compute_name

    main(
        subscription_id,
        resource_group_name,
        workspace_name,
        name,
        endpoint_name,
        model_name,
        compute_name,
    )
