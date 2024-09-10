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
from azure.identity import DefaultAzureCredential
import argparse
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import MLClient, Input
from azure.ai.ml import load_component
import time
import os
from mlops.common.get_compute import get_compute
from mlops.common.get_environment import get_environment
from mlops.common.config_utils import MLOpsConfig
from mlops.common.naming_utils import (
    generate_experiment_name,
    generate_model_name,
    generate_run_name,
)


gl_pipeline_components = []


@pipeline()
def london_taxi_data_regression(pipeline_job_input, model_name, build_reference):
    """
    Run a pipeline for regression analysis on NYC taxi data.

    Parameters:
    pipeline_job_input (str): Path to the input data.
    model_name (str): Name of the model.
    build_reference (str): Reference for the build.

    Returns:
    dict: A dictionary containing paths to various data, the model, predictions, and score report.
    """
    prepare_sample_data = gl_pipeline_components[0](
        raw_data=pipeline_job_input,
    )
    transform_sample_data = gl_pipeline_components[1](
        clean_data=prepare_sample_data.outputs.prep_data,
    )
    train_with_sample_data = gl_pipeline_components[2](
        training_data=transform_sample_data.outputs.transformed_data,
    )
    predict_with_sample_data = gl_pipeline_components[3](
        model_input=train_with_sample_data.outputs.model_output,
        test_data=train_with_sample_data.outputs.test_data,
    )
    score_with_sample_data = gl_pipeline_components[4](
        predictions=predict_with_sample_data.outputs.predictions,
        model=train_with_sample_data.outputs.model_output,
    )
    gl_pipeline_components[5](
        model_metadata=train_with_sample_data.outputs.model_metadata,
        model_name=model_name,
        score_report=score_with_sample_data.outputs.score_report,
        build_reference=build_reference,
    )

    return {
        "pipeline_job_prepped_data": prepare_sample_data.outputs.prep_data,
        "pipeline_job_transformed_data": transform_sample_data.outputs.transformed_data,
        "pipeline_job_trained_model": train_with_sample_data.outputs.model_output,
        "pipeline_job_test_data": train_with_sample_data.outputs.test_data,
        "pipeline_job_predictions": predict_with_sample_data.outputs.predictions,
        "pipeline_job_score_report": score_with_sample_data.outputs.score_report,
    }


def construct_pipeline(
    cluster_name: str,
    environment_name: str,
    display_name: str,
    build_environment: str,
    build_reference: str,
    model_name: str,
    dataset_name: str,
    ml_client,
):
    """
    Construct a pipeline job for NYC taxi data regression.

    Args:
        cluster_name (str): The name of the cluster to use for pipeline execution.
        environment_name (str): The name of the environment to use for pipeline execution.
        display_name (str): The display name of the pipeline job.
        build_environment (str): The environment to deploy the pipeline job.
        build_reference (str): The build reference for the pipeline job.
        model_name (str): The name of the model.
        dataset_name (str): The name of the dataset.
        ml_client: The machine learning client.

    Returns:
        pipeline_job: The constructed pipeline job.
    """
    registered_data_asset = ml_client.data.get(name=dataset_name, label="latest")

    parent_dir = os.path.join(os.getcwd(), "mlops/london_taxi/components")

    prepare_data = load_component(source=parent_dir + "/prep.yml")
    transform_data = load_component(source=parent_dir + "/transform.yml")
    train_model = load_component(source=parent_dir + "/train.yml")
    predict_result = load_component(source=parent_dir + "/predict.yml")
    score_data = load_component(source=parent_dir + "/score.yml")
    register_model = load_component(source=parent_dir + "/register.yml")

    # Set the environment name to custom environment using name and version number
    prepare_data.environment = environment_name
    transform_data.environment = environment_name
    train_model.environment = environment_name
    predict_result.environment = environment_name
    score_data.environment = environment_name
    register_model.environment = environment_name

    gl_pipeline_components.append(prepare_data)
    gl_pipeline_components.append(transform_data)
    gl_pipeline_components.append(train_model)
    gl_pipeline_components.append(predict_result)
    gl_pipeline_components.append(score_data)
    gl_pipeline_components.append(register_model)

    pipeline_job = london_taxi_data_regression(
        Input(type="uri_folder", path=registered_data_asset.id),
        model_name,
        build_reference,
    )

    pipeline_job.display_name = display_name
    pipeline_job.tags = {
        "environment": build_environment,
        "build_reference": build_reference,
    }

    # demo how to change pipeline output settings
    pipeline_job.outputs.pipeline_job_prepped_data.mode = "rw_mount"

    # set pipeline level compute
    pipeline_job.settings.default_compute = cluster_name
    pipeline_job.settings.force_rerun = True
    # set pipeline level datastore
    pipeline_job.settings.default_datastore = "workspaceblobstore"

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
        wait_for_completion (str): "True" or "False" - indicates whether to wait for the job to complete.
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

            if pipeline_job.status == "Completed" or pipeline_job.status == "Finished":
                print("job completed")
            else:
                raise Exception("Sorry, exiting job with failure..")
    except Exception as ex:
        print(
            "Oops! invalid credentials or error while creating ML environment.. Try again...",
            ex,
        )
        raise


def prepare_and_execute(
    build_environment: str,
    wait_for_completion: str,
    output_file: str,
):
    """
    Prepare and execute the MLOps pipeline.

    Args:
        build_environment (str): environment name to execute.
        wait_for_completion (str): "True" or "False" - indicates whether to wait for the job to complete.
        output_file (str): The path to the output file where the job name will be written.
    """
    model_name = "london_taxi"

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
        compute.name,
        f"azureml:{environment.name}:{environment.version}",
        published_run_name,
        build_environment,
        config.environment_configuration["build_reference"],
        published_model_name,
        pipeline_config["dataset_name"],
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


def main():
    """Parse the command line arguments and call the `prepare_and_execute` function."""
    parser = argparse.ArgumentParser("build_environment")
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
    args = parser.parse_args()

    prepare_and_execute(
        args.build_environment, args.wait_for_completion, args.output_file
    )


if __name__ == "__main__":
    main()
