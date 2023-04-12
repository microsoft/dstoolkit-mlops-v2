"""
It should be executed as a module from a working folder
example: python -m mlops.nyc_taxi.start_nyc_local
"""
from dotenv import load_dotenv
import subprocess
import os
import uuid
from mlops.nyc_taxi.src.mlops_pipeline import prepare_and_execute


def main():
    print("Loading environment variables")
    load_dotenv()

    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")
    workspace_name = os.environ.get("WORKSPACE_NAME")
    cluster_name = os.environ.get("CLUSTER_NAME")
    cluster_size = os.environ.get("CLUSTER_SIZE")
    cluster_region = os.environ.get("CLUSTER_REGION")
    build_id = os.environ.get("BUILD.BUILDID")
    deploy_environment = os.environ.get("DEPLOY_ENVIRONMENT")
    experiment_base_name = os.environ.get("EXPERIMENT_BASE_NAME")
    display_base_name = os.environ.get("DISPLAY_BASE_NAME")
    wait_for_completion = os.environ.get("WAIT_FOR_COMPLETION")
    environment_name = os.environ.get("ENVIRONMENT_NAME")
    env_base_image_name = os.environ.get("ENV_BASE_IMAGE_NAME")
    conda_path = os.environ.get("CONDA_PATH")

    git_branch = subprocess.check_output(
        "git rev-parse --abbrev-ref HEAD", shell=True, universal_newlines=True
    ).strip()
    git_branch_items = git_branch.split("/")
    git_branch = git_branch_items[len(git_branch_items) - 1]

    experiment_name = f"nyc_{experiment_base_name}_{git_branch}"
    display_name = f"nyc_{display_base_name}_{uuid.uuid4().hex}"

    print("Start pipeline creation")

    prepare_and_execute(
        subscription_id,
        resource_group_name,
        workspace_name,
        cluster_name,
        cluster_size,
        cluster_region,
        0,
        4,
        1200,
        env_base_image_name,
        conda_path,
        environment_name,
        "my test environment",
        wait_for_completion,
        display_name,
        experiment_name,
        deploy_environment,
        build_id,
        None,
    )


if __name__ == "__main__":
    main()
