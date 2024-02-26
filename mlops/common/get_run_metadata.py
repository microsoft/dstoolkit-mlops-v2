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

from mlops.common.config_utils import MLOpsConfig


def get_run_metadata(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    run_id: str,
    output_file_name: str,
):
    """
    Get information about a job run and save information into a file.

    This is an utility method that is going to be used in DevOps pipelines.

    Parameters:
      subscription_id (str): a subscription id where the workspace is located
      resource_group_name (str): a resource group where the workspace is located
      workspace_name (str): name of the Azure ML workspace
      run_id (str): id of the run to check
      output_file_name (str): a path to a file to save the results
    """
    client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )
    my_run = client.jobs.get(run_id)

    metadata = {
        "job_url": my_run.studio_url,
        "aml_display_name": my_run.display_name,
        "aml_run_name": my_run.experiment_name,
        "aml_run_id": my_run.id,
        "aml_name": my_run.name,
    }

    if output_file_name is not None:
        with open(output_file_name, "w") as out_file:
            out_file.write(json.dumps(metadata))


def main():
    """
    Get information about a job run and save information into a file.

    This is an entry point to invoke get_run_metadata from the command line interface.
    """
    parser = argparse.ArgumentParser("get_run_metadata")
    parser.add_argument("--run_id", type=str, help="get metadata for the run_id")
    parser.add_argument(
        "--output_file_name", type=str, help="output file containing run metadata"
    )

    args = parser.parse_args()

    config = MLOpsConfig()

    get_run_metadata(
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
        args.run_id,
        args.output_file_name,
    )


if __name__ == "__main__":
    main()
