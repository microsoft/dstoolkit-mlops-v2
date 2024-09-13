"""This module is designed for registering machine learning models in MLflow."""

import argparse
import json
import logging
import pathlib
import shutil
import yaml
from azureml.core.run import Run

import src.sequence_model.common.mlflow_ext as mlflow

logger = logging.getLogger(__name__)
run_tags = {"model": "sequence_model", "step": "register"}


def parse_args():
    """Parse arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser("register_model")

    parser.add_argument(
        "--model_config",
        type=str,
        required=True,
        help="Configuration file for the sequence model.",
    )

    parser.add_argument(
        "--model_name", type=str, help="Name of model to be registered."
    )

    parser.add_argument(
        "--score_report_folder",
        type=str,
        help="Location of score report of model",
    )

    parser.add_argument(
        "--model_artifacts",
        type=str,
        required=True,
        default=None,
        help="Path with serialized model components",
    )

    parser.add_argument(
        "--benchmark_report_folder", type=str, help="Folder container benchmark report."
    )

    parser.add_argument(
        "--predictions_folder",
        type=str,
        required=True,
        default=None,
        help="Location of serialized set of model predictions on test data",
    )

    return parser.parse_args()


def assemble_outputs(args):
    """
    Assemble and organize output artifacts for model registration.

    This function creates necessary directories and copies various files into a single folder structure
    for easier model registration. It consolidates predictions, model artifacts, score reports, and benchmark
    reports into designated folders.

    Parameters:
    args (argparse.Namespace): Command-line arguments containing paths to the predictions folder, model artifacts,
                               score report folder, and benchmark report folder.

    Returns:
    tuple: A tuple containing the paths to the artifacts folder and the model registration folder.
    """
    artifacts_folder = pathlib.Path("artifacts/")
    pathlib.Path(artifacts_folder).mkdir(exist_ok=True)
    model_registration_folder = pathlib.Path(artifacts_folder, "model_registration/")
    pathlib.Path(model_registration_folder).mkdir(exist_ok=True)

    # Copy files to single folder
    shutil.copytree(args.predictions_folder, artifacts_folder, dirs_exist_ok=True)

    shutil.copytree(args.model_artifacts, model_registration_folder, dirs_exist_ok=True)
    shutil.copytree(
        args.score_report_folder, model_registration_folder, dirs_exist_ok=True
    )
    shutil.copytree(
        args.benchmark_report_folder, model_registration_folder, dirs_exist_ok=True
    )

    return artifacts_folder, model_registration_folder


def register(args, model_name: str):  # #model_folder: str, score_report_path: str):
    """Register model.

    Args:
        model_name (str): Name of model.
        model_path (str): Path to model.
        score_report_path (str): Path to model scoring report.
    """
    run = Run.get_context()

    artifacts_folder, _ = assemble_outputs(args)

    run = Run.get_context()
    run.upload_folder("artifacts", str(artifacts_folder))

    run.register_model(
        model_path="artifacts/model_registration",
        model_name=model_name,
        description="A next token prediction model using the prior n-grams to infer the next word.",
    )

    logger.info(
        f"Completed model Registration! Registered version new version of model: {model_name}"
    )


if __name__ == "__main__":
    try:
        args = parse_args()

        score_report_path = pathlib.Path(args.score_report_folder) / "score_report.json"
        benchmark_report_path = (
            pathlib.Path(args.benchmark_report_folder) / "benchmark.json"
        )

        benchmark_report_data = json.load(open(benchmark_report_path))

        # Load sequence model yaml configuration
        cfg = None
        with open(args.model_config) as config_file:
            cfg = yaml.safe_load(config_file)

        # Get configurations
        logging_cfg = cfg["logging"]
        mlflow_cfg = cfg["mlflow"]

        # Configure console logging.
        logging.config.dictConfig(logging_cfg)

        # Configure MLFlow
        current_id, parent_run_id = mlflow.init_run(
            command_line_args=args, run_tags=run_tags, mlflow_config=mlflow_cfg
        )

        mlflow.set_tags(benchmark_report_data)

        if benchmark_report_data.get("register_model", True):
            register(args, args.model_name)
    except Exception as ex:
        print(
            "Registering Model Failed",
            ex,
        )
        raise
