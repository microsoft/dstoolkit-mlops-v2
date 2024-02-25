"""
This module provides functionalities for testing a machine learning model deployed on Azure.

The script requires various arguments like subscription ID, resource group name, workspace name,
data purpose, data configuration path, environment name, and batch configuration path to be provided.
It uses these arguments to connect to Azure Machine Learning services using MLClient, retrieves
the specified dataset, and invokes a batch endpoint for model testing.
"""

import argparse
import json

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, Input
from azure.ai.ml.constants import AssetTypes

from mlops.common.config_utils import MLOpsConfig



parser = argparse.ArgumentParser("provision_deployment")
parser.add_argument("--model_type", type=str, help="registered model type to be deployed", required=True)
parser.add_argument("--env_type", type=str, help="env name (dev, test, prod) for deployment", required=True)
parser.add_argument("--run_id", type=str, help="AML run id for model generation", required=True)
args = parser.parse_args()

config = MLOpsConfig()

ml_client = MLClient(
    DefaultAzureCredential(),
    config.aml_config["subscription_id"],
    config.aml_config["resource_group_name"],
    config.aml_config["workspace_name"]
)

model_type = args.model_type
run_id = args.run_id
env_type = args.env_type

dataset_unlabeled = ml_client.data.get(name=dataset_name, label="latest")

input = Input(type=AssetTypes.URI_FOLDER, path=dataset_unlabeled.id)

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
