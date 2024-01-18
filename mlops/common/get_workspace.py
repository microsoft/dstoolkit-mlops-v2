"""
This module provides utilities for accessing and managing an Azure Machine Learning workspace.

It includes functionality to authenticate with Azure using default credentials and to retrieve
information about a specified Azure Machine Learning workspace. This is particularly useful
for automated scripts that need to interact with Azure ML resources, ensuring they can
securely access the necessary workspace.
"""
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential


def get_workspace(subscription_id: str, resource_group_name: str, workspace_name: str):
    """
    Return a reference to the workspace object.

    Parameters:
      subscription_id (str): a subscription id where the workspace is located
      resource_group_name (str): a resource group where the workspace is located
      workspace_name (str): name of the workspace

    Returns:
        Workspace: an object that represents the workspace
    """
    try:
        print(f"Getting access to {workspace_name} workspace.")
        client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )

        workspace = client.workspaces.get(workspace_name)
        print(f"Reference to {workspace_name} has been obtained.")
        return workspace
    except Exception as ex:
        print("Oops!  invalid credentials.. Try again...", ex)
        raise
