"""
This module is designed to register data assets in an Azure Machine Learning environment.

It utilizes the Azure AI MLClient from the Azure Machine Learning SDK to interact with Azure resources.
The module parses command-line arguments to receive necessary details like subscription ID, resource group name,
workspace name, data purpose, data configuration path, and environment name.

The script reads a configuration file to identify and register datasets in Azure Machine Learning based on their purpose
and the specified environment (development, test, production, etc.). It supports operations like creating or updating
data assets and retrieving the latest version of these assets.
"""

import argparse
import json

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

from mlops.common.config_utils import MLOpsConfig

config = MLOpsConfig()

#ml_client = MLClient(
#    DefaultAzureCredential(),
#    config.aml_config["subscription_id"],
#    config.aml_config["resource_group_name"],
#    config.aml_config["workspace_name"]
#)

parser = argparse.ArgumentParser("register data assets")

parser.add_argument("--subscription_id", type=str, help="Azure subscription id", required=True)
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group", required=True)
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name", required=True)
parser.add_argument("--data_purpose", type=str, help="data to be registered identified by purpose", required=True)
parser.add_argument("--data_config_path", type=str, help="data config file path", required=True)
parser.add_argument("--environment_name", type=str, help="environment name (e.g. dev, test, prod)", required=True)
parser.add_argument("--api_version", type=str, help="API version to use (optional)")

args = parser.parse_args()

data_purpose = args.data_purpose
data_config_path = args.data_config_path
environment_name = args.environment_name

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name,
    api_version=args.api_version
)

config_file = open("mlops/nyc_taxi/configs/data_config.json")
#config_file = open(data_config_path)
data_config = json.load(config_file)

for elem in data_config['datasets']:
    if 'DATA_PURPOSE' in elem and 'ENV_NAME' in elem:
        if data_purpose == elem["DATA_PURPOSE"] and environment_name == elem['ENV_NAME']:
            data_path = elem["DATA_PATH"]
            dataset_desc = elem["DATASET_DESC"]
            dataset_name = elem["DATASET_NAME"]

            aml_dataset = Data(
                path=data_path,
                type=AssetTypes.URI_FOLDER,
                description=dataset_desc,
                name=dataset_name,
            )

            ml_client.data.create_or_update(aml_dataset)

            aml_dataset_unlabeled = ml_client.data.get(name=dataset_name, label="latest")

            print(aml_dataset_unlabeled.latest_version)
            print(aml_dataset_unlabeled.id)