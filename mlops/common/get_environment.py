from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import argparse
from azure.ai.ml.entities import Environment


def get_environment(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    env_base_image_name: str,
    conda_path: str,
    environment_name: str,
    description: str,
):
    try:
        print(f"Checking {environment_name} environment.")
        client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )
        env_docker_conda = Environment(
            image=env_base_image_name,
            conda_file=conda_path,
            name=environment_name,
            description=description,
        )
        environment = client.environments.create_or_update(env_docker_conda)
        print(f"Environment {environment_name} has been created or updated.")
        return environment

    except Exception as ex:
        print(
            "Oops! invalid credentials or error while creating ML environment.. Try again..."
        )
        raise


def main():
    parser = argparse.ArgumentParser("prepare_environment")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )
    parser.add_argument(
        "--env_base_image_name", type=str, help="Environment custom base image name"
    )
    parser.add_argument(
        "--conda_path", type=str, help="path to conda requirements file"
    )
    parser.add_argument(
        "--environment_name", type=str, help="Azure Machine learning environment name"
    )
    parser.add_argument(
        "--description", type=str, default="Environment created using Conda."
    )
    args = parser.parse_args()

    get_environment(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.env_base_image_name,
        args.conda_path,
        args.environment_name,
        args.description,
    )


if __name__ == "__main__":
    main()
