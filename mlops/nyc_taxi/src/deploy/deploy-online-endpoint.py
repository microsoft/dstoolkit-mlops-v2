import argparse

from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment
from azure.identity import DefaultAzureCredential


def main(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    deployment_name: str,
    endpoint_name: str,
    model_name: str,
    instance_type: str,
    instance_count: int,
    traffic_allocation: int,
):
    print("Get AML Workspace handler...")
    ml_client = MLClient(
        DefaultAzureCredential(), subscription_id, resource_group_name, workspace_name
    )

    print("Deploy online endpoint...")
    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name,
        description="this is a sample online endpoint",
        auth_mode="key",
    )

    ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    print("Deploying to endpoint...")
    blue_deployment = ManagedOnlineDeployment(
        name=name,
        endpoint_name=endpoint_name,
        model=model_name + "@latest",
        instance_type=instance_type,
        instance_count=instance_count,
    )

    ml_client.online_deployments.begin_create_or_update(blue_deployment).result()

    print("Update deployment traffic...")
    endpoint.traffic = {name: traffic_allocation}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create online deployment")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
    parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
    parser.add_argument("--deployment_name", type=str, help="Name of online deployment")
    parser.add_argument("--endpoint_name", type=str, help="Name of the online endpoint")
    parser.add_argument("--model_name", type=str, help="AML model name")
    parser.add_argument("--instance_type", type=str, help="Instance type", default="Standard_DS3_v2")
    parser.add_argument("--instance_count", type=int, help="Instance count", default=1)
    parser.add_argument("--traffic_allocation", type=int,help="Deployment traffic allocation percentage", default=0)

    args = parser.parse_args()

    subscription_id = args.subscription_id
    resource_group_name = args.resource_group_name
    workspace_name = args.workspace_name
    name = args.deployment_name
    endpoint_name = args.endpoint_name
    model_name = args.model_name
    instance_type = args.instance_type
    instance_count = args.instance_count
    traffic_allocation = args.traffic_allocation

    main(
        subscription_id,
        resource_group_name,
        workspace_name,
        name,
        endpoint_name,
        model_name,
        instance_type,
        instance_count,
        traffic_allocation,
    )
