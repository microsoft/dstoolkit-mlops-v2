import os
import json
from pathlib import Path
import argparse
import random
import string
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint
)
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import (
    BatchEndpoint,
    ModelBatchDeployment,
    ModelBatchDeploymentSettings,
    Model,
    AmlCompute,
    Data,
    BatchRetrySettings,
    CodeConfiguration,
    Environment,
)
from azure.ai.ml.constants import AssetTypes, BatchDeploymentOutputAction

# arguments expected for executing the experiments
parser = argparse.ArgumentParser("provision_endpoints")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--realtime_deployment_config", type=str, help="Azureml realtime config")
parser.add_argument("--run_id", type=str, help="run responsbile for model generation")
parser.add_argument("--build_id", type=str, help="build responsbile for deployment")
parser.add_argument("--is_batch", type=str, help="batch endpoint provisioning")
parser.add_argument("--batch_config", type=str, help="file path to batch config")
parser.add_argument("--environment_name",type=str,help="data config path")
args = parser.parse_args()



batch = args.is_batch
build_id = args.build_id
run_id = args.run_id
batch_config = args.batch_config
real_config = args.realtime_deployment_config
environment_name = args.environment_name

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name
)

if batch == "False":
    config_file = open(real_config)
    endpoint_config = json.load(config_file)
    for elem in endpoint_config['real_time']:
        if 'ENDPOINT_NAME' in elem and 'ENV_NAME' in elem:
            if environment_name == elem['ENV_NAME']:
                endpoint_name = elem["ENDPOINT_NAME"]

                endpoint = ManagedOnlineEndpoint(
                    name=endpoint_name,
                    description="An online endpoint serving an MLflow model for the diabetes classification task",
                    auth_mode="key",
                    tags={"build_id": build_id, "run_id": run_id},
                )

                ml_client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

else:
    config_file = open(batch_config)
    endpoint_config = json.load(config_file)
    for elem in endpoint_config['batch_config']:
        if 'ENDPOINT_NAME' in elem and 'ENV_NAME' in elem:
            if environment_name == elem['ENV_NAME']:
                endpoint_name = elem["ENDPOINT_NAME"]
                
                endpoint = BatchEndpoint(
                    name=endpoint_name,
                    description="A heart condition classifier for batch inference",
                    tags={"build_id": build_id, "run_id": run_id},
                )

                ml_client.batch_endpoints.begin_create_or_update(endpoint).result()