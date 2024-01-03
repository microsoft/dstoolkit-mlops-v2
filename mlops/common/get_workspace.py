"""
This module provides utilities for accessing and managing an Azure Machine Learning workspace.

It includes functionality to authenticate with Azure using default credentials and to retrieve 
information about a specified Azure Machine Learning workspace. This is particularly useful 
for automated scripts that need to interact with Azure ML resources, ensuring they can 
securely access the necessary workspace.
"""
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import argparse


def get_workspace(subscription_id: str, resource_group_name: str, workspace_name: str):
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


def main():
    parser = argparse.ArgumentParser("get_workspace")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )

    args = parser.parse_args()
    get_workspace(args.subscription_id, args.resource_group_name, args.workspace_name)


if __name__ == "__main__":
    main()
