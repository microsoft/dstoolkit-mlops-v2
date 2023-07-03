import argparse
import os
import json
from azure.ai.ml import MLClient, Input
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential

parser = argparse.ArgumentParser("test_model")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--data_purpose", type=str, help="data to be registered identified by purpose")
parser.add_argument("--data_config_path", type=str, help="data config path")
parser.add_argument("--deployment_name", type=str, help="AML deployment name")
parser.add_argument("--endpoint_name", type=str, help="AML endpoint name")
parser.add_argument("--environment_name",type=str,help="data config path")

args = parser.parse_args()

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id,  args.resource_group_name,  args.workspace_name
)
data_purpose = args.data_purpose
data_config_path = args.data_config_path
environment_name = args.environment_name

config_file = open(data_config_path)
data_config = json.load(config_file)

for elem in data_config['datasets']:
    if 'DATA_PURPOSE' in elem and 'ENV_NAME' in elem:
        if data_purpose == elem["DATA_PURPOSE"] and environment_name == elem['ENV_NAME']:
            dataset_name = elem["DATASET_NAME"]

            heart_dataset_unlabeled = ml_client.data.get(name=dataset_name, label="latest")

            input = Input(type=AssetTypes.URI_FOLDER, path=heart_dataset_unlabeled.id)

            job = ml_client.batch_endpoints.invoke(
                deployment_name=args.deployment_name, endpoint_name=args.endpoint_name, input=input
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