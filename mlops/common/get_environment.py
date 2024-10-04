"""
This module is designed to facilitate the creation and management of Azure Machine Learning environments.

It leverages the Azure AI ML Client for communicating with Azure ML services, enabling users to create or
update machine learning environments in an Azure subscription. The module provides functionality to
authenticate with Azure, define environment specifications, and perform environment setup or updates.
"""

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Environment


def get_environment(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    env_base_image_name: str,
    conda_path: str,
    environment_name: str,
    description: str = "Azure ML environment",
):
    """
    Create or update Azure ML environment and return a reference to it.

    Parameters:
      subscription_id (str): a subscription id where the workspace is located
      resource_group_name (str): a resource group where the workspace is located
      workspace_name (str): name of the Azure ML workspace
      env_base_image_name (str): a name of the base image for the environment
      conda_path (str): a path to a conda file with additional packages to install
      environment_name (str): a name of the environment
      description (str): a description of the environment

    Returns:
      Environment: an object that represents the environment
    """
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
            "Oops! invalid credentials or error while creating ML environment.. Try again...",
            ex,
        )
        raise
