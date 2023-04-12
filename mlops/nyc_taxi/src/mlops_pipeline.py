from azure.identity import DefaultAzureCredential
import argparse
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import MLClient, Input
from azure.ai.ml import load_component
import time
import os
from mlops.common.get_compute import get_compute
from mlops.common.get_environment import get_environment


gl_pipeline_components = []


@pipeline()
def nyc_taxi_data_regression(pipeline_job_input, model_name, build_reference):
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
    register_model_with_sample_data = gl_pipeline_components[5](
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
    deploy_environment: str,
    build_reference: str,
    model_name: str,
):
    parent_dir = os.path.join(os.getcwd(), "mlops/nyc_taxi/components")
    data_dir = os.path.join(os.getcwd(), "mlops/nyc_taxi/data/")

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

    pipeline_job = nyc_taxi_data_regression(
        Input(type="uri_folder", path=data_dir), model_name, build_reference
    )
    pipeline_job.display_name = display_name
    pipeline_job.tags = {
        "environment": deploy_environment,
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
            "Oops! invalid credentials or error while creating ML environment.. Try again..."
        )
        raise


def prepare_and_execute(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    cluster_name: str,
    cluster_size: str,
    cluster_region: str,
    min_instances: int,
    max_instances: int,
    idle_time_before_scale_down: int,
    env_base_image_name: str,
    conda_path: str,
    environment_name: str,
    env_description: str,
    wait_for_completion: str,
    display_name: str,
    experiment_name: str,
    deploy_environment: str,
    build_reference: str,
    model_name: str,
    output_file: str,
):
    compute = get_compute(
        subscription_id,
        resource_group_name,
        workspace_name,
        cluster_name,
        cluster_size,
        cluster_region,
        min_instances,
        max_instances,
        idle_time_before_scale_down,
    )

    environment = get_environment(
        subscription_id,
        resource_group_name,
        workspace_name,
        env_base_image_name,
        conda_path,
        environment_name,
        env_description,
    )

    print(f"Environment: {environment.name}, version: {environment.version}")

    pipeline_job = construct_pipeline(
        compute.name,
        f"azureml:{environment.name}:{environment.version}",
        display_name,
        deploy_environment,
        build_reference,
        model_name,
    )

    execute_pipeline(
        subscription_id,
        resource_group_name,
        workspace_name,
        experiment_name,
        pipeline_job,
        wait_for_completion,
        output_file,
    )


def main():
    parser = argparse.ArgumentParser("build_environment")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )
    parser.add_argument(
        "--cluster_name", type=str, help="Azure Machine learning cluster name"
    )
    parser.add_argument(
        "--cluster_size", type=str, help="Azure Machine learning cluster size"
    )
    parser.add_argument(
        "--cluster_region", type=str, help="Azure Machine learning cluster region"
    )
    parser.add_argument("--min_instances", type=int, default=0)
    parser.add_argument("--max_instances", type=int, default=4)
    parser.add_argument("--idle_time_before_scale_down", type=int, default=120)
    parser.add_argument(
        "--build_reference",
        type=str,
        help="Unique identifier for Azure DevOps pipeline run",
    )
    parser.add_argument(
        "--deploy_environment",
        type=str,
        help="execution and deployment environment. e.g. dev, prod, test",
    )
    parser.add_argument(
        "--experiment_name", type=str, help="Job execution experiment name"
    )
    parser.add_argument("--display_name", type=str, help="Job execution run name")
    parser.add_argument(
        "--wait_for_completion",
        type=str,
        help="determine if pipeline to wait for job completion",
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        help="Azure Machine Learning Environment name for job execution",
    )
    parser.add_argument(
        "--env_base_image_name", type=str, help="Environment custom base image name"
    )
    parser.add_argument(
        "--conda_path", type=str, help="path to conda requirements file"
    )
    parser.add_argument(
        "--env_description", type=str, default="Environment created using Conda."
    )
    parser.add_argument(
        "--model_name", type=str, default="Name used for registration of model"
    )
    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run id"
    )

    args = parser.parse_args()

    prepare_and_execute(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.cluster_name,
        args.cluster_size,
        args.cluster_region,
        args.min_instances,
        args.max_instances,
        args.idle_time_before_scale_down,
        args.env_base_image_name,
        args.conda_path,
        args.environment_name,
        args.env_description,
        args.wait_for_completion,
        args.display_name,
        args.experiment_name,
        args.deploy_environment,
        args.build_reference,
        args.model_name,
        args.output_file,
    )


if __name__ == "__main__":
    main()
