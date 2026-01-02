"""
This module is designed for provisioning Azure Machine Learning endpoints.

It utilizes the Azure ML SDK (MLClient) to create or update batch endpoints in an Azure ML workspace.
"""
import argparse
import time
from azure.ai.ml import MLClient
from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import BatchEndpoint
from mlops.common.config_utils import MLOpsConfig


def wait_for_endpoint_ready(ml_client, endpoint_name, max_wait=600):
    """Wait for endpoint to be ready for operations."""
    print(f"Checking if endpoint {endpoint_name} is ready for operations...")
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            endpoint = ml_client.batch_endpoints.get(endpoint_name)
            print(f"Endpoint state: {endpoint.provisioning_state}")

            if endpoint.provisioning_state == "Succeeded":
                print(f"Endpoint {endpoint_name} is ready")
                return True
            elif endpoint.provisioning_state in ["Failed", "Canceled"]:
                raise Exception(f"Endpoint in {endpoint.provisioning_state} state")
            else:
                print(f"Endpoint still provisioning ({endpoint.provisioning_state}). Waiting 30 seconds...")
                time.sleep(30)
        except Exception as e:
            if "not found" in str(e).lower() or "ResourceNotFound" in str(e):
                print(f"Endpoint {endpoint_name} does not exist yet - ready to create")
                return True
            raise

    raise TimeoutError(f"Endpoint not ready after {max_wait} seconds")


def create_with_retry(ml_client, endpoint, max_retries=3, initial_delay=60):
    """Create endpoint with retry logic for concurrent operation conflicts."""
    for attempt in range(max_retries):
        try:
            print(f"Endpoint creation attempt {attempt + 1}/{max_retries}...")
            poller = ml_client.batch_endpoints.begin_create_or_update(endpoint)
            result = poller.result()
            print("Endpoint creation completed successfully")
            return result
        except ResourceExistsError as e:
            if "operation is already in progress" in str(e).lower() and attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)  # Exponential backoff
                print("Conflict detected: Another operation is in progress on endpoint.")
                print(f"Waiting {delay} seconds before retry {attempt + 2}/{max_retries}...")
                time.sleep(delay)
            else:
                print(f"Endpoint creation failed after {attempt + 1} attempts")
                raise
        except Exception as e:
            print(f"Unexpected error during endpoint creation: {str(e)}")
            raise

    raise Exception("Endpoint creation failed after all retry attempts")


def main():
    """Create Azure ML endpoint."""
    parser = argparse.ArgumentParser("provision_endpoint")
    parser.add_argument(
        "--model_type", type=str, help="registered model type to be deployed", required=True
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        help="env name (dev, test, prod) for deployment",
        required=True,
    )
    parser.add_argument(
        "--run_id", type=str, help="AML run id for model generation", required=True
    )
    args = parser.parse_args()

    model_type = args.model_type
    run_id = args.run_id
    env_type = args.environment_name

    config = MLOpsConfig(environment=env_type)

    ml_client = MLClient(
        DefaultAzureCredential(),
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
    )

    deployment_key = f"{model_type}_batch"
    try:
        deployment_config = config.get_deployment_config(deployment_name=deployment_key)
    except KeyError as err:
        available = ", ".join(sorted(config.deployment_configs.keys()))
        print(
            f"Deployment config not found for key '{deployment_key}_{env_type}'. "
            f"Available deployment_configs keys: {available}"
        )
        raise err

    if not deployment_config:
        raise ValueError(
            f"Deployment config '{deployment_key}_{env_type}' is empty or null in config.yaml"
        )

    endpoint = BatchEndpoint(
        name=deployment_config["endpoint_name"],
        description=deployment_config["endpoint_desc"],
        tags={
            "build_id": config.environment_configuration["build_reference"],
            "run_id": run_id,
        },
    )

    # Wait for any existing operations to complete
    wait_for_endpoint_ready(ml_client, deployment_config["endpoint_name"])

    # Create endpoint with retry logic
    create_with_retry(ml_client, endpoint)


if __name__ == "__main__":
    main()
