"""
This module defines a machine learning pipeline for processing, training, and evaluating data.

The pipeline executes the following steps in order:
1. Prepare Sample Data: Preprocesses raw data to make it suitable for further processing and analysis.
2. Transform Sample Data: Performs advanced data transformations such as feature engineering.
3. Train with Sample Data: Trains a machine learning model using the transformed data.
4. Predict with Sample Data: Uses the trained model to make predictions on new data.
5. Score with Sample Data: Evaluates the model's performance based on its predictions.
6. Finalize and Persist Model: Handles tasks like persisting model metadata, registering the model,
and generating reports.
"""

import argparse
import os
import time

import mlflow
from azure.ai.ml import Input, MLClient, load_component
from azure.ai.ml.dsl import pipeline
from azure.identity import DefaultAzureCredential

from mlops.common.config_utils import MLOpsConfig
from mlops.common.get_compute import get_compute
from mlops.common.get_environment import get_environment
from mlops.common.naming_utils import (
    generate_experiment_name,
    generate_model_name,
    generate_run_name,
)

gl_pipeline_components = []


@pipeline()
def sequence_model_pipeline(
    pipeline_job_input,
    model_name,
):
    """
    Run a pipeline for training and scoring of sequence model.

    Parameters:
    pipeline_job_input (str): Path to the input data.
    model_name (str): Name of the model.
    build_reference (str): Reference for the build.

    Returns:
    dict: A dictionary containing paths to various data, the model, predictions, and score report.
    """
    train_model_cmp = gl_pipeline_components[0](
        dataset_folder=pipeline_job_input,
    )
    predict_model_cmp = gl_pipeline_components[1](
        dataset_folder=pipeline_job_input,
        model_artifacts=train_model_cmp.outputs.model_artifacts,
    )
    score_model_cmp = gl_pipeline_components[2](
        predictions_folder=predict_model_cmp.outputs.predictions_folder,
    )

    benchmark_model_cmp = gl_pipeline_components[3](
        score_report_folder=score_model_cmp.outputs.score_report_folder,
    )

    gl_pipeline_components[4](
        model_name=model_name,
        score_report_folder=score_model_cmp.outputs.score_report_folder,
        benchmark_report_folder=benchmark_model_cmp.outputs.benchmark_report_folder,
        model_artifacts=train_model_cmp.outputs.model_artifacts,
        predictions_folder=predict_model_cmp.outputs.predictions_folder,
    )

    return {
        "pipeline_job_model": train_model_cmp.outputs.model_artifacts,
        "pipeline_job_predictions": predict_model_cmp.outputs.predictions_folder,
        "pipeline_job_model_score": score_model_cmp.outputs.score_report_folder,
        "pipeline_job_benchmark": benchmark_model_cmp.outputs.benchmark_report_folder,
    }


def construct_pipeline(
    triggered_by: str,
    cluster_name: str,
    environment_name: str,
    display_name: str,
    build_environment: str,
    build_reference: str,
    model_name: str,
    dataset_uri_folder: str,
    ml_client,
):
    """
    Construct a pipeline job for sequence model training and scoring.

    Args:
        cluster_name (str): The name of the cluster to use for pipeline execution.
        environment_name (str): The name of the environment to use for pipeline execution.
        display_name (str): The display name of the pipeline job.
        build_environment (str): The environment to deploy the pipeline job.
        build_reference (str): The build reference for the pipeline job.
        model_name (str): The name of the model.
        dataset_uri_folder (str): The name of the dataset.
        ml_client: The machine learning client.

    Returns:
        pipeline_job: The constructed pipeline job.
    """
    registered_data_asset = ml_client.data.get(name=dataset_uri_folder, label="latest")

    training_dataset_type = registered_data_asset.tags.get("dataset_type", "NotDefined")

    parent_dir = os.path.join(os.getcwd(), "mlops/sequence_model/components")

    # Train Model
    train_model = load_component(source=parent_dir + "/train.yml")
    train_model.environment = environment_name
    gl_pipeline_components.append(train_model)

    # Predict Model
    predict_result = load_component(source=parent_dir + "/predict.yml")
    predict_result.environment = environment_name
    gl_pipeline_components.append(predict_result)

    # Score Model
    score_data = load_component(source=parent_dir + "/score.yml")
    score_data.environment = environment_name
    gl_pipeline_components.append(score_data)

    # Benchmark Model
    benchmark_model = load_component(source=parent_dir + "/benchmark.yml")
    benchmark_model.environment = environment_name
    gl_pipeline_components.append(benchmark_model)

    # Register Model
    register_model_cmp = load_component(source=parent_dir + "/register.yml")
    register_model_cmp.environment = environment_name
    gl_pipeline_components.append(register_model_cmp)

    pipeline_job = sequence_model_pipeline(
        pipeline_job_input=Input(type="uri_folder", path=registered_data_asset.id),
        model_name=model_name,
    )

    pipeline_job.display_name = display_name
    pipeline_job.tags = {
        "environment": build_environment,
        "build_reference": build_reference,
        "triggered_by": triggered_by,
        "dataset": dataset_uri_folder,
        "dataset_type": training_dataset_type,
    }

    # demo how to change pipeline output settings
    # pipeline_job.outputs.pipeline_job_prepped_data.mode = "rw_mount"
    # set pipeline level compute
    pipeline_job.settings.default_compute = cluster_name
    pipeline_job.settings.force_rerun = True
    # set pipeline level datastore
    pipeline_job.settings.default_datastore = "workspaceblobstore"
    return pipeline_job


def write_metadata(
    client: MLClient, job_name: str, output_file_path: str = None
) -> dict:
    """Write metadata to env or file.

    Args:
        client (MLClient): Current ml client
        job_name (str): Name of job.
        output_file_path (str, optional): Where to right file it not env. Defaults to None.
    """
    current_job = client.jobs.get(job_name)

    mlflow_tracking_uri = client.workspaces.get(
        client.workspace_name
    ).mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    exp = mlflow.get_experiment_by_name(current_job.experiment_name)

    file_path = os.getenv("GITHUB_ENV", output_file_path)
    print('file_path', file_path)
    metadata = {
        "job_url": current_job.studio_url,
        "aml_display_name": current_job.display_name,
        "aml_run_name": current_job.experiment_name,
        "aml_run_id": current_job.id,
        "aml_name": current_job.name,
        "register_model": exp.tags.get("register_model"),
        "benchmarks_met": exp.tags.get("benchmarks_met"),
        "best_accuracy": exp.tags.get("best_accuracy"),
    }

    if file_path:
        with open(file_path, "a") as env_file:
            for key, value in metadata.items():
                env_file.write(f"{key.upper()}={value}\n")

    return metadata


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

        if wait_for_completion == "True":
            total_wait_time = 172800
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
                    print("Job Status:", pipeline_job.status)
                    current_wait_time = current_wait_time + 15
                    if (
                        pipeline_job.status == "Failed"
                        or pipeline_job.status == "NotResponding"
                        or pipeline_job.status == "CancelRequested"
                        or pipeline_job.status == "Canceled"
                    ):
                        break
                else:
                    break

            metadata = write_metadata(client, pipeline_job.name, output_file)

            if pipeline_job.status == "Completed" or pipeline_job.status == "Finished":
                print("job completed")
            else:
                if metadata.get("benchmarks_met") == "False":
                    raise Exception("Model Benchmarking failed!")
                elif metadata.get("best_accuracy") == "False":
                    raise Exception("Model did not match or outperform prior model!")
                else:
                    raise Exception("Sorry, exiting job with failure..")
    except Exception as ex:
        print(
            "An error occurred.  Please visit docs/how-to/Troubleshooting.md for more info on troubleshooting.",
            ex,
        )
        raise


def prepare_and_execute(
    triggered_by: str,
    build_environment: str,
    wait_for_completion: str,
    output_file: str,
):
    """
    Prepare and execute the MLOps pipeline.

    Args:
        build_environment (str): environment name to execute.
        wait_for_completion (str): "True" or "False" indicates whether to wait for the job to complete.
        output_file (str): The path to the output file where the job name will be written.
    """
    model_name = "sequence_model"
    config = MLOpsConfig(environment=build_environment)
    ml_client = MLClient(
        DefaultAzureCredential(),
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
    )
    pipeline_config = config.get_pipeline_config(model_name)
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
        config.environment_configuration["env_base_image"],
        pipeline_config["conda_path"],
        pipeline_config["aml_env_name"],
    )
    print(f"Environment: {environment.name}, version: {environment.version}")
    published_model_name = generate_model_name(model_name)
    published_experiment_name = generate_experiment_name(model_name)
    published_run_name = generate_run_name(
        config.environment_configuration["build_reference"]
    )
    pipeline_job = construct_pipeline(
        triggered_by,
        compute.name,
        f"azureml:{environment.name}:{environment.version}",
        published_run_name,
        build_environment,
        config.environment_configuration["build_reference"],
        published_model_name,
        pipeline_config["dataset_uri_folder"],
        ml_client,
    )
    execute_pipeline(
        config.aml_config["subscription_id"],
        config.aml_config["resource_group_name"],
        config.aml_config["workspace_name"],
        published_experiment_name,
        pipeline_job,
        wait_for_completion,
        output_file,
    )


def parse_args() -> argparse.Namespace:
    """Parse arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser("build_environment")

    parser.add_argument(
        "--triggered_by",
        type=str,
        help="Who triggered the pipeline",
    )

    parser.add_argument(
        "--build_environment",
        type=str,
        help="configuration environment for the pipeline",
    )
    parser.add_argument(
        "--wait_for_completion",
        type=str,
        help="determine if pipeline to wait for job completion",
        default="True",
    )

    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run id"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    prepare_and_execute(
        args.triggered_by,
        args.build_environment,
        args.wait_for_completion,
        args.output_file,
    )
