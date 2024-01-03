"""
This module provides functionality to retrieve and store metadata for a specific Azure Machine Learning run.

It utilizes the Azure ML SDK to interact with an Azure Machine Learning workspace and extract metadata 
related to a specified run. The metadata includes various details such as the run's URL, display name, 
experiment name, and other relevant information.
"""
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import argparse
import json


def get_run_metadata(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    run_id: str,
    output_file_name: str,
):

    client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )
    my_run = client.jobs.get(run_id)

    metadata = {}
    metadata["job_url"] = my_run.studio_url
    metadata["aml_display_name"] = my_run.display_name
    metadata["aml_run_name"] = my_run.experiment_name
    metadata["aml_run_id"] = my_run.id
    metadata["aml_name"] = my_run.name
    metadata["job_url"] = my_run.studio_url
    metadata["job_url"] = my_run.studio_url
    metadata["job_url"] = my_run.studio_url

    if output_file_name is not None:
        with open(output_file_name, "w") as out_file:
            out_file.write(json.dumps(metadata))


def main():
    parser = argparse.ArgumentParser("get_run_metadata")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )
    parser.add_argument(
        "--run_id", type=str, help="get metadata for the run_id"
    )
    parser.add_argument(
        "--output_file_name", type=str, help="output file containing run metadata"
    )

    args = parser.parse_args()

    get_run_metadata(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.run_id,
        args.output_file_name,
    )


if __name__ == "__main__":
    main()
