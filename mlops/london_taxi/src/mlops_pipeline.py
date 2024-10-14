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
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import Input
from azure.ai.ml import load_component
import os
from mlops.common.config_utils import MLOpsConfig
from mlops.common.naming_utils import generate_model_name
from mlops.common.pipeline_job_config import PipelineJobConfig
from mlops.common.pipeline_utils import prepare_and_execute_pipeline

gl_pipeline_components = []


@pipeline()
def london_taxi_data_regression(pipeline_job_input: Input, model_name: str, build_reference: str):
    """
    Run a pipeline for regression analysis on London taxi data.

    Args:
        pipeline_job_input (Input): The raw input data for the pipeline.
        model_name (str): The name of the model to be used.
        build_reference (str): A reference identifier for the build.

    Returns:
        dict: A dictionary containing the outputs of various stages of the pipeline:
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


class LondonTaxi(PipelineJobConfig):
    """
    Class for the London taxi data Azure ML pipeline configuration and construction.

    This class extends the Pipeline class and provides specific implementations for the London taxi data
    regression pipeline. It includes methods for constructing the pipeline.
    """

    def construct_pipeline(self, ml_client):
        """
        Construct a pipeline job for London taxi data regression.

        Args:
            ml_client: The Azure ML client to use for retrieving data assets and components.

        Returns:
            pipeline_job: The constructed pipeline job components.
        """
        registered_data_asset = ml_client.data.get(
            name=self.dataset_name, label="latest"
        )

        parent_dir = os.path.join(os.getcwd(), "mlops/london_taxi/components")

        components = ["prep", "transform", "train", "predict", "score", "register"]

        for component in components:
            comp = load_component(source=f"{parent_dir}/{component}.yml")
            comp.environment = self.environment_name
            gl_pipeline_components.append(comp)

        pipeline_job = london_taxi_data_regression(
            Input(type="uri_folder", path=registered_data_asset.id),
            self.model_name,
            self.build_reference,
        )

        # demo how to change pipeline output settings
        pipeline_job.outputs.pipeline_job_prepped_data.mode = "rw_mount"

        return pipeline_job


def prepare_and_execute(
    model_name: str, build_environment: str, wait_for_completion: bool, output_file: str
):
    """
    Prepare and execute the pipeline.

    Args:
        model_name (str): The name of the model.
        build_environment (str): The build environment configuration.
        wait_for_completion (bool): Whether to wait for the pipeline job to complete.
        output_file (str): A file to save the run ID.
    """
    config = MLOpsConfig(environment=build_environment)

    pipeline_config = config.get_pipeline_config(model_name)
    published_model_name = generate_model_name(model_name)

    pipeline_job_config = LondonTaxi(
        environment_name=None,  # will be set in prepare_and_execute_pipeline
        build_reference=config.environment_configuration["build_reference"],
        published_model_name=published_model_name,
        dataset_name=pipeline_config["dataset_name"],
        build_environment=build_environment,
        wait_for_completion=wait_for_completion,
        output_file=output_file,
        model_name=model_name,
    )

    prepare_and_execute_pipeline(pipeline_job_config)


def main():
    """Parse the command line arguments and call the `prepare_and_execute` function."""
    parser = argparse.ArgumentParser("build_environment")
    parser.add_argument(
        "--model_name", type=str, help="name of the model", default="london_taxi"
    )
    parser.add_argument(
        "--build_environment",
        type=str,
        help="configuration environment for the pipeline",
    )
    parser.add_argument(
        "--wait_for_completion",
        type=bool,
        help="determine if pipeline should wait for job completion",
        default=True,
    )
    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run id"
    )
    args = parser.parse_args()

    prepare_and_execute(
        args.model_name,
        args.build_environment,
        args.wait_for_completion,
        args.output_file,
    )


if __name__ == "__main__":
    main()
