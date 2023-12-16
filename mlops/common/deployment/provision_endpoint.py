
import json
import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint
)
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import (
    BatchEndpoint
)

parser = argparse.ArgumentParser("provision_endpoints")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id", required=True)
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group", required=True)
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name", required=True)
parser.add_argument("--realtime_deployment_config", type=str, help="file path of realtime config")
parser.add_argument("--run_id", type=str, help="AML run id for model generation", required=True)
parser.add_argument("--build_id", type=str, help="Azure DevOps build id for deployment", required=True)
parser.add_argument("--is_batch", type=str, help="Endpoint Type: True for batch; False for real-time", required=True)
parser.add_argument("--batch_config", type=str, help="file path of batch config")
parser.add_argument("--environment_name",type=str,help="environment name (e.g. dev, test, prod)", required=True)
args = parser.parse_args()

batch = args.is_batch
build_id = args.build_id
run_id = args.run_id
if args.batch_config is not None:
    batch_config = args.batch_config
if args.realtime_deployment_config is not None:
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
                endpoint_desc = elem["ENDPOINT_DESC"]
                endpoint = ManagedOnlineEndpoint(
                    name=endpoint_name,
                    description=endpoint_desc,
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
                    description="model with batch endpoint",
                    tags={"build_id": build_id, "run_id": run_id},
                )

                ml_client.batch_endpoints.begin_create_or_update(endpoint).result()
                