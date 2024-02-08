"""
This module provides functionalities for testing a machine learning model deployed on Azure.

The script requires various arguments like subscription ID, resource group name, workspace name,
data purpose, data configuration path, environment name, and batch configuration path to be provided.
It uses these arguments to connect to Azure Machine Learning services using MLClient, retrieves
the specified dataset, and invokes a batch endpoint for model testing.
"""

import argparse
import json
from azure.ai.ml import MLClient, Input
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential

parser = argparse.ArgumentParser("test_model")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id", required=True)
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group", required=True)
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name", required=True)
parser.add_argument("--data_purpose", type=str, help="type of data to be registered e.g. training, test", required=True)
parser.add_argument("--data_config_path", type=str, help="data config path", required=True)
parser.add_argument("--environment_name", type=str, help="env name (dev, test, prod) for deployment", required=True)
parser.add_argument("--batch_config", type=str, help="file path of batch config", required=True)

args = parser.parse_args()

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name
)
data_purpose = args.data_purpose
data_config_path = args.data_config_path
environment_name = args.environment_name
batch_config = args.batch_config

config_file = open(data_config_path)
data_config = json.load(config_file)

batch_file = open(batch_config)
batch_data = json.load(batch_file)
input = None

for elem in data_config['datasets']:
    if 'DATA_PURPOSE' in elem and 'ENV_NAME' in elem:
        if data_purpose == elem["DATA_PURPOSE"] and environment_name == elem['ENV_NAME']:
            dataset_name = elem["DATASET_NAME"]

            dataset_unlabeled = ml_client.data.get(name=dataset_name, label="latest")

            input = Input(type=AssetTypes.URI_FOLDER, path=dataset_unlabeled.id)

for elem in batch_data['batch_config']:
    if 'ENDPOINT_NAME' in elem and 'ENV_NAME' in elem:
        if environment_name == elem["ENV_NAME"]:
            endpoint_name = elem["ENDPOINT_NAME"]
            deployment_name = elem["DEPLOYMENT_NAME"]

            print("deployment_name:", deployment_name)
            print("endpoint_name:", endpoint_name)
            job = ml_client.batch_endpoints.invoke(
                deployment_name=deployment_name, endpoint_name=endpoint_name, input=input
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
