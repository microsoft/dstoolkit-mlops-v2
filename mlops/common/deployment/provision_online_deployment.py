"""
This script automates the deployment of machine learning models in Azure Machine Learning.

It supports real-time deployment scenarios.
"""
import argparse
import time
import json
import requests
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineDeployment,
    Environment,
    CodeConfiguration,
)
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceExistsError
from mlops.common.config_utils import MLOpsConfig
from mlops.common.naming_utils import generate_model_name


def _fetch_and_save_async_operation(uri, credential):
    """Fetch the Azure async operation payload and save it to a file for diagnostics."""
    if not uri:
        print("No AzureAsyncOperationUri available to fetch.")
        return

    try:
        token = credential.get_token("https://management.azure.com/.default").token
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print(f"Fetching Azure async operation payload from: {uri}")
        resp = requests.get(uri, headers=headers, timeout=30)
        try:
            payload = resp.json()
            pretty = json.dumps(payload, indent=2)
        except Exception:
            pretty = resp.text

        print("--- AzureAsyncOperation payload ---")
        print(pretty)

        try:
            with open("deployment_async_operation.json", "w", encoding="utf-8") as fh:
                fh.write(pretty)
            print("Wrote async operation payload to deployment_async_operation.json")
        except Exception as e:
            print(f"Unable to write async op payload to file: {e}")
    except Exception as e:
        print(f"Failed to fetch Azure async operation payload: {e}")


def wait_for_endpoint_ready(ml_client, endpoint_name, max_wait=600):
    """Wait for endpoint to be ready for operations."""
    print(f"Checking if endpoint {endpoint_name} is ready for operations...")
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            endpoint = ml_client.online_endpoints.get(endpoint_name)
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


def _dump_deployment_diagnostics(ml_client, endpoint_name, deployment_name):
    """Fetch and print deployment diagnostics for failed/canceled deployments."""
    try:
        detailed = ml_client.online_deployments.get(
            name=deployment_name, endpoint_name=endpoint_name
        )
        print("--- Deployment diagnostic dump ---")
        try:
            print(detailed)
        except Exception:
            print(repr(detailed))

        # Fetch Azure async operation payload for deeper diagnostics
        _try_fetch_async_operation(detailed)
    except Exception:
        print(f"Unable to fetch detailed deployment info for {deployment_name}")


def _try_fetch_async_operation(deployment_obj):
    """Attempt to fetch and save Azure async operation payload."""
    try:
        credential = DefaultAzureCredential()
        async_uri = None
        props = getattr(deployment_obj, "properties", None)
        if props:
            try:
                async_uri = props.get("AzureAsyncOperationUri")
            except Exception:
                async_uri = getattr(props, "AzureAsyncOperationUri", None)
        if not async_uri:
            async_uri = getattr(deployment_obj, "AzureAsyncOperationUri", None)

        if async_uri:
            _fetch_and_save_async_operation(async_uri, credential)
    except Exception:
        print("Unable to fetch Azure async operation payload for diagnostics")


def wait_for_deployment_ready(
    ml_client, endpoint_name, deployment_name, max_wait=900, poll_interval=30
):
    """Ensure the existing deployment finishes any in-flight operation before updating."""
    print(
        f"Checking if deployment {deployment_name} on endpoint "
        f"{endpoint_name} is idle before updating..."
    )
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            deployment = ml_client.online_deployments.get(
                name=deployment_name, endpoint_name=endpoint_name
            )
            state = getattr(deployment, "provisioning_state", None)

            if not state or state == "Succeeded":
                print(
                    f"Deployment {deployment_name} is in '{state or 'Unknown'}' "
                    f"state and ready for updates"
                )
                return True
            if state in ["Failed", "Canceled"]:
                _dump_deployment_diagnostics(ml_client, endpoint_name, deployment_name)
                raise Exception(
                    f"Deployment {deployment_name} in {state} state - "
                    f"manual intervention required"
                )

            print(
                f"Deployment {deployment_name} still provisioning ({state}). "
                f"Waiting {poll_interval} seconds before re-check..."
            )
            time.sleep(poll_interval)
        except Exception as e:
            message = str(e)
            if "resourcenotfound" in message.lower() or "not found" in message.lower():
                print(
                    f"Deployment {deployment_name} does not exist yet - "
                    f"safe to create a new deployment"
                )
                return True
            raise

    raise TimeoutError(
        f"Deployment {deployment_name} still not ready after {max_wait} seconds"
    )


def _handle_deployment_conflict(attempt, max_retries, initial_delay, wait_if_conflict):
    """Handle deployment conflict by waiting or using exponential backoff."""
    print("Conflict detected: Another operation is in progress.")
    if wait_if_conflict:
        print("Waiting for existing deployment operation to finish before retrying...")
        wait_if_conflict()
    else:
        delay = initial_delay * (2 ** attempt)
        print(f"Waiting {delay} seconds before retry {attempt + 2}/{max_retries}...")
        time.sleep(delay)


def _dump_current_deployment_state(ml_client, deployment):
    """Try to fetch and print current deployment status for diagnostics."""
    try:
        dep_name = getattr(deployment, 'name', None)
        ep_name = getattr(deployment, 'endpoint_name', None)
        if dep_name and ep_name:
            current = ml_client.online_deployments.get(
                name=dep_name, endpoint_name=ep_name
            )
            print("--- Current deployment state dump ---")
            try:
                print(current)
            except Exception:
                print(repr(current))
            _try_fetch_async_operation(current)
    except Exception:
        print("Could not retrieve live deployment state for diagnostics")


def deploy_with_retry(
    ml_client,
    deployment,
    max_retries=3,
    initial_delay=60,
    wait_if_conflict=None,
):
    """Deploy with retry logic for concurrent operation conflicts."""
    for attempt in range(max_retries):
        try:
            print(f"Deployment attempt {attempt + 1}/{max_retries}...")
            poller = ml_client.begin_create_or_update(deployment)
            result = poller.result()
            print("Deployment completed successfully")
            return result
        except ResourceExistsError as e:
            message = str(e)
            if "Already running method" in message and attempt < max_retries - 1:
                _handle_deployment_conflict(attempt, max_retries, initial_delay, wait_if_conflict)
            else:
                print(f"Deployment failed after {attempt + 1} attempts")
                raise
        except Exception as e:
            print(f"Unexpected error during deployment: {str(e)}")
            _dump_current_deployment_state(ml_client, deployment)
            raise

    raise Exception("Deployment failed after all retry attempts")


def main():
    """Automate the deployment of machine learning models in Azure Machine Learning."""
    parser = argparse.ArgumentParser("provision_deployment")
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

    deployment_config = config.get_deployment_config(deployment_name=f"{model_type}_online")

    published_model_name = generate_model_name(model_type)

    print(f"Looking for model: {published_model_name}")

    try:
        model_refs = ml_client.models.list(published_model_name)
        model_list = list(model_refs)

        if not model_list:
            print(f"ERROR: No models found with name '{published_model_name}'")
            print("Available models:")
            for model in ml_client.models.list():
                print(f"  - {model.name} (version {model.version})")
            raise ValueError(
                f"Model '{published_model_name}' not found. "
                "Please check model name and ensure training completed successfully."
            )

        latest_version = max(model.version for model in model_list)
        print(f"Found model version: {latest_version}")
        model = ml_client.models.get(published_model_name, latest_version)
    except Exception as e:
        print(f"Error retrieving model '{published_model_name}': {str(e)}")
        raise

    environment = Environment(
        conda_file=deployment_config["deployment_conda_path"],
        image=deployment_config["deployment_base_image"],
    )

    blue_deployment = ManagedOnlineDeployment(
        name=deployment_config["deployment_name"],
        endpoint_name=deployment_config["endpoint_name"],
        model=model,
        description=deployment_config["deployment_desc"],
        environment=environment,
        code_configuration=CodeConfiguration(
            code=deployment_config["score_dir"],
            scoring_script=deployment_config["score_file_name"],
        ),
        instance_type=deployment_config["deployment_vm_size"],
        instance_count=deployment_config["deployment_instance_count"],
        tags={
            "build_id": config.environment_configuration["build_reference"],
            "run_id": run_id,
        },
    )

    # Wait for endpoint and deployment to be idle before deploying
    wait_for_endpoint_ready(ml_client, deployment_config["endpoint_name"])
    wait_for_deployment_ready(
        ml_client,
        deployment_config["endpoint_name"],
        deployment_config["deployment_name"],
    )

    # Deploy with retry logic
    def wait_callback():
        return wait_for_deployment_ready(
            ml_client,
            deployment_config["endpoint_name"],
            deployment_config["deployment_name"],
        )

    deploy_with_retry(
        ml_client,
        blue_deployment,
        wait_if_conflict=wait_callback,
    )


if __name__ == "__main__":
    main()
