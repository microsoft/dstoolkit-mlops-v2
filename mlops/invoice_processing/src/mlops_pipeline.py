"""
This module defines a machine learning pipeline for processing, training, and evaluating data.

The pipeline executes the following steps in order:
1. Prepare Sample Data: Preprocesses raw data to make it suitable for further processing and analysis.
2. Predict with Sample Data: Uses the trained model to make predictions on new data.
3. Score with Sample Data: Evaluates the model's performance based on its predictions.
"""

import argparse
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import Input
from azure.ai.ml import load_component
import os
import yaml

from mlops.common.config_utils import MLOpsConfig
from mlops.common.naming_utils import generate_model_name
from mlops.common.pipeline_job_config import PipelineJobConfig
from mlops.common.pipeline_utils import prepare_and_execute_pipeline

gl_pipeline_components = []


@pipeline()
def invoice_processing_data_regression(
    pipeline_job_input: Input,
    model_name: str,
    build_reference: str,
    strategy: str,
    temperature: float,
    gpt_deployment_name: str,
    prompt_config: str,
    ground_truth_data: Input,
    score_config: str,
    samples_amount: int,
    sampling_seed: int,
):
    """
    Run a pipeline for regression analysis on invoice data.

    Args:
        pipeline_job_input (Input): The raw input data for the pipeline.
        model_name (str): The name of the model to be used.
        build_reference (str): A reference identifier for the build.
        gpt_deployment_name(str): GPT Deployment name.
        strategy(str): strategy for predict step e.g. prompt
        prompt_config(str): config to use for predict step e.g. prompt
        ground_truth_data(Input): ground truth input
        score_config (str): dictionary loaded from file as string
        samples_amount (int): amount of samples to randomly use from the data set, 0 means all
        sampling_seed (int): seed for random sampling of dataset, -1 means no seed

    Returns:
        dict: A dictionary containing the outputs of various stages of the pipeline:
    """
    prepare_sample_data = gl_pipeline_components[0](
        raw_data=pipeline_job_input,
        samples_amount=samples_amount,
        sampling_seed=sampling_seed,
    )
    predict_with_sample_data = gl_pipeline_components[1](
        strategy=strategy,
        temperature=temperature,
        gpt_deployment_name=gpt_deployment_name,
        prompt_config=prompt_config,
        test_data=prepare_sample_data.outputs.prep_data,
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
    score_with_sample_data = gl_pipeline_components[2](
        predictions=predict_with_sample_data.outputs.predictions,
        ground_truth=ground_truth_data,
        score_config=score_config,
    )

    pipeline_outputs = {
        "pipeline_job_prepped_data": prepare_sample_data.outputs.prep_data,
        "pipeline_job_predictions": predict_with_sample_data.outputs.predictions,
        "pipeline_job_score_report": score_with_sample_data.outputs.score_report,
        "pipeline_job_missing_refs": score_with_sample_data.outputs.missing_refs,
        "pipeline_job_all_unmatched_gt": score_with_sample_data.outputs.all_unmatched_gt,
        "pipeline_job_all_unmatched_pred": score_with_sample_data.outputs.all_unmatched_pred,
    }

    return pipeline_outputs


@pipeline()
def invoice_processing_score_only(
    pipeline_job_input: Input,
    model_name: str,
    build_reference: str,
    strategy: str,
    gpt_deployment_name: str,
    prompt_config: str,
    ground_truth_data: Input,
    score_config: str,
    samples_amount: int,
    sampling_seed: int,
    predictions_file: Input,
    temperature: float,
):
    """
    Run a pipeline for regression analysis on invoice data.

    Args:
        pipeline_job_input (Input): The raw input data for the pipeline.
        model_name (str): The name of the model to be used.
        build_reference (str): A reference identifier for the build.
        gpt_deployment_name(str): GPT Deployment name you used to generate the predictions.
        strategy(str): strategy which was used for predictions generated.
        prompt_config(str): prompt config which was used for predictions generated.
        ground_truth_data(Input): ground truth input
        score_config (str): dictionary loaded from file as string
        samples_amount (int): amount of samples to randomly use from the data set, 0 means all
        sampling_seed (int): seed for random sampling of dataset, -1 means no seed
        predictions (Input): predictions generated previously.

    Returns:
        dict: A dictionary containing the outputs of various stages of the pipeline:
    """
    score_with_sample_data = gl_pipeline_components[2](
        predictions=predictions_file,
        ground_truth=ground_truth_data,
        score_config=score_config,
    )

    pipeline_outputs = {
        "pipeline_job_score_report": score_with_sample_data.outputs.score_report,
        "pipeline_job_missing_refs": score_with_sample_data.outputs.missing_refs,
        "pipeline_job_all_unmatched_gt": score_with_sample_data.outputs.all_unmatched_gt,
        "pipeline_job_all_unmatched_pred": score_with_sample_data.outputs.all_unmatched_pred,
    }

    return pipeline_outputs


class InvoiceProcessing(PipelineJobConfig):
    """
    Class for the invoice processing data Azure ML pipeline configuration and construction.

    This class extends the Pipeline class and provides specific implementations for the invoice processing data
    regression pipeline. It includes methods for constructing the pipeline.
    """

    def construct_pipeline(self, ml_client):
        """
        Construct a pipeline job for invoice data regression.

        Args:
            ml_client: The Azure ML client to use for retrieving data assets and components.

        Returns:
            pipeline_job: The constructed pipeline job components.
        """
        registered_data_asset = ml_client.data.get(
            name=self.dataset_name, label="latest"
        )

        registered_gt_asset = ml_client.data.get(name=self.gt_name, label="latest")

        parent_dir = os.path.join(os.getcwd(), "mlops/invoice_processing/components")

        components = ["prep", "predict", "score"]

        for component in components:
            comp = load_component(source=f"{parent_dir}/{component}.yml")
            comp.environment = self.environment_name
            gl_pipeline_components.append(comp)

        experiment_config = yaml.safe_load(open("config/experiment_config.yaml"))

        pipeline_inputs = {
            "pipeline_job_input": Input(
                type="uri_folder", path=registered_data_asset.id
            ),
            "model_name": self.model_name,
            "build_reference": self.build_reference,
            "strategy": (experiment_config["predict_config"])["strategy"],
            "temperature": (experiment_config["predict_config"])["temperature"],
            "gpt_deployment_name": (experiment_config["predict_config"])[
                "gpt_deployment_name"
            ],
            "prompt_config": str(
                (experiment_config["predict_config"])["prompt_config"]
            ),
            "ground_truth_data": Input(type="uri_folder", path=registered_gt_asset.id),
            "score_config": str(experiment_config["score_config"]),
            "samples_amount": (experiment_config["prep_config"])["samples_amount"],
            "sampling_seed": (experiment_config["prep_config"])["sampling_seed"],
        }

        if self.predictions is not None:
            prediction_file = ml_client.data.get(name=self.predictions, label="latest")
            pipeline_inputs["predictions_file"] = Input(
                type="uri_folder", path=prediction_file.id
            )
            pipeline_job = invoice_processing_score_only(**pipeline_inputs)
        else:
            pipeline_job = invoice_processing_data_regression(**pipeline_inputs)

        # demo how to change pipeline output settings
        # pipeline_job.outputs.pipeline_job_prepped_data.mode = "rw_mount"

        return pipeline_job


def prepare_and_execute(
    model_name: str,
    build_environment: str,
    wait_for_completion: str,
    output_file: str,
    predictions: str = None,
):
    """
    Prepare and execute the pipeline.

    Args:
        model_name (str): The name of the model.
        build_environment (str): The build environment configuration.
        wait_for_completion (str): Whether to wait for the pipeline job to complete.
        output_file (str): A file to save the run ID.
    """
    config = MLOpsConfig(environment=build_environment)

    pipeline_config = config.get_pipeline_config(model_name)
    published_model_name = generate_model_name(model_name)
    experiment_description = config.get_experiment_description()

    pipeline_job_config = InvoiceProcessing(
        environment_name=None,  # will be set in prepare_and_execute_pipeline
        build_reference=config.environment_configuration["build_reference"],
        published_model_name=published_model_name,
        dataset_name=pipeline_config["dataset_name"],
        gt_name=pipeline_config["gt_name"],
        build_environment=build_environment,
        wait_for_completion=wait_for_completion,
        output_file=output_file,
        model_name=model_name,
        predictions=predictions,
    )

    prepare_and_execute_pipeline(pipeline_job_config, experiment_description)


def main():
    """Parse the command line arguments and call the `prepare_and_execute` function."""
    parser = argparse.ArgumentParser("build_environment")
    parser.add_argument(
        "--model_name", type=str, help="name of the model", default="invoice_processing"
    )
    parser.add_argument(
        "--build_environment",
        type=str,
        help="configuration environment for the pipeline",
    )
    parser.add_argument(
        "--wait_for_completion",
        type=str,
        help="determine if pipeline should wait for job completion",
        default="True",
    )
    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run id"
    )
    parser.add_argument(
        "--predictions", type=str, required=False, help="Name of the predictions file"
    )

    args = parser.parse_args()

    prepare_and_execute(
        args.model_name,
        args.build_environment,
        args.wait_for_completion,
        args.output_file,
        args.predictions,
    )


if __name__ == "__main__":
    main()
