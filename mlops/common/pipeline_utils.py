"""
This module defines a machine learning pipeline for processing, training, and evaluating data.
"""
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import MLClient
import time

from mlops.common.config_utils import MLOpsConfig
from mlops.common.get_compute import get_compute
from mlops.common.get_environment import get_environment
from mlops.common.naming_utils import generate_experiment_name, generate_run_name, generate_environment_name


def set_pipeline_properties(
    pipeline_job: pipeline,
    cluster_name: str,
    display_name: str,
    tags: dict,
    default_datastore: str = "workspaceblobstore",
    force_rerun: bool = True
):
    """
    Set properties for the pipeline job.

    Args:
        pipeline_job (pipeline): The pipeline job to set properties for.
        cluster_name (str): The name of the compute cluster.
        display_name (str): The display name for the pipeline job.
        tags (dict): A dictionary of key-value pairs to set as tags for the pipeline job.
        default_datastore (str, optional): The default datastore for the pipeline job. Defaults to "workspaceblobstore".
        force_rerun (bool, optional): Whether to force rerun the pipeline job. Defaults to True.

    Returns:
        pipeline: The updated pipeline job with the specified properties.
    """

    pipeline_job.display_name = display_name
    pipeline_job.tags = tags

    # set pipeline level compute
    pipeline_job.settings.default_compute = cluster_name
    pipeline_job.settings.force_rerun = force_rerun
    # set pipeline level datastore
    pipeline_job.settings.default_datastore = default_datastore

    return pipeline_job

def execute_pipeline(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    experiment_name: str,
    pipeline_job: pipeline,
    wait_for_completion: str,
    output_file: str,
):
    """
    Execute a pipeline job in Azure Machine Learning service.

    Args:
        subscription_id (str): The Azure subscription ID.
        resource_group_name (str): The name of the resource group.
        workspace_name (str): The name of the Azure Machine Learning workspace.
        experiment_name (str): The name of the experiment.
        pipeline_job (pipeline): The pipeline job to be executed.
        wait_for_completion (str): "True" or "False" indicates whether to wait for the job to complete.
        output_file (str): The path to the output file where the job name will be written.

    Raises:
        Exception: If the job fails to complete.

    Returns:
        None
    """
    try:
        client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )

        pipeline_job = client.jobs.create_or_update(
            pipeline_job, experiment_name=experiment_name
        )

        print(f"The job {pipeline_job.name} has been submitted!")
        if output_file is not None:
            with open(output_file, "w") as out_file:
                out_file.write(pipeline_job.name)

        if wait_for_completion == "True":
            total_wait_time = 3600
            current_wait_time = 0
            job_status = [
                "NotStarted",
                "Queued",
                "Starting",
                "Preparing",
                "Running",
                "Finalizing",
                "Provisioning",
                "CancelRequested",
                "Failed",
                "Canceled",
                "NotResponding",
            ]

            while pipeline_job.status in job_status:
                if current_wait_time <= total_wait_time:
                    time.sleep(20)
                    pipeline_job = client.jobs.get(pipeline_job.name)

                    print(f"Job Status: {pipeline_job.status}")

                    current_wait_time = current_wait_time + 15

                    if (
                        pipeline_job.status == "Failed"
                        or pipeline_job.status == "NotResponding"
                        or pipeline_job.status == "CancelRequested"
                        or pipeline_job.status == "Canceled"
                    ):
                        print(
                            f"Pipeline job '{pipeline_job.name}' has stopped with status: {pipeline_job.status}."
                        )
                        break
                else:
                    print(
                        f"Job {pipeline_job.name} exceeded the wait time limit of 1 hour."
                    )
                    break

            if pipeline_job.status == "Completed" or pipeline_job.status == "Finished":
                print("Job completed successfully.")
            else:
                raise Exception(
                    f"Job {pipeline_job.name} did not complete successfully. "
                    f"Current status: {pipeline_job.status}"
                )
    except ClientAuthenticationError as auth_ex:
        print(
            "Authorization error occurred while executing the pipeline."
            "Please check your credentials and permissions."
            f"Error details: {auth_ex}"
        )
        raise
    except Exception as ex:
        print(
            "An error occurred while executing the pipeline."
            "Please check your credentials, resource details, and job configuration."
            f"Error details: {ex}"
        )
        raise


def prepare_and_execute_pipeline(pipeline):

    config = MLOpsConfig(environment=pipeline.build_environment)
    pipeline_config = config.get_pipeline_config(pipeline.model_name)

    ml_client = MLClient(
        DefaultAzureCredential(),
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
    )

    compute = get_compute(
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
        pipeline_config["cluster_name"],
        pipeline_config["cluster_size"],
        pipeline_config["cluster_region"],
    )

    environment = get_environment(
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
        env_base_image=config.environment_configuration["env_base_image"],
        environment_name=pipeline_config["aml_env_name"],
        docker_context_path=pipeline_config.get("docker_context_path", None),
        dockerfile_path=pipeline_config.get("dockerfile_path", None),
        conda_path=pipeline_config.get("conda_path", None),
    )

    published_experiment_name = generate_experiment_name(pipeline.model_name)
    published_run_name = generate_run_name(config.environment_configuration["build_reference"])
    environment_name = generate_environment_name(environment.name, environment.version)

    pipeline.environment_name = environment_name

    pipeline_job = pipeline.construct_pipeline(ml_client)

    pipeline_job_tags = {
        "environment": pipeline.build_environment,
        "build_reference": pipeline.model_name,
    }

    pipeline_job = set_pipeline_properties(
        pipeline_job,
        cluster_name=compute.name,
        display_name=published_run_name,
        tags=pipeline_job_tags
    )

    execute_pipeline(
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
        published_experiment_name,
        pipeline_job,
        pipeline.wait_for_completion,
        pipeline.output_file,
    )
