
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import mlflow
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
    azureml_mlflow_uri = client.workspaces.get(workspace_name).mlflow_tracking_uri
    mlflow.set_tracking_uri(azureml_mlflow_uri)

    my_run = mlflow.get_run(run_id)

    metadata = {}
    metadata["aml_uri"] = my_run.info.artifact_uri
    metadata["aml_run_name"] = my_run.info.run_name
    metadata["aml_run_id"] = my_run.info.run_uuid
    metadata["aml_experiment_id"] = my_run.info.experiment_id

    if output_file_name is not None:
        with open(output_file_name, "w") as out_file:
            out_file.write(json.dumps(metadata))
    print(my_run)



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
