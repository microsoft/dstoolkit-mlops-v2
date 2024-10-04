"""
This module is designed for model benchmarking.

It is intended to be expanded upon and customized for future models.
"""
import json
import logging
import logging.config
from argparse import ArgumentParser, Namespace
from pathlib import Path

import yaml
from azureml.core.model import Model
from azureml.core.run import Run

import src.sequence_model.common.mlflow_ext as mlflow

logger = logging.getLogger(__name__)
run_tags = {"model": "sequence_model", "step": "benchmark"}


def parse_args() -> Namespace:
    """Parse arguments.

    Returns:
        Namespace: _description_
    """
    parser = ArgumentParser("benchmark_model")

    parser.add_argument(
        "--model_config",
        type=str,
        required=True,
        help="Configuration file for the sequence model.",
    )

    parser.add_argument(
        "--score_report_folder", type=str, help="Folder container score report."
    )

    parser.add_argument(
        "--benchmark_report_folder", type=str, help="Folder container benchmark report."
    )

    return parser.parse_args()


def parse_json_file(file_path: str) -> dict:
    """Parse json file.

    Args:
        file_path (str): Path to json file.

    Returns:
        dict: Parsed json as dictionary.
    """
    json_data = {}
    with open(file_path) as file:
        json_data = json.load(file)
    return json_data


def parse_yaml_file(file_path: str) -> dict:
    """Parse yaml file.

    Args:
        file_path (str): Path to yaml file.

    Returns:
        dict: Parsed yaml as dictionary.
    """
    yaml_data = {}
    with open(file_path) as file:
        yaml_data = yaml.safe_load(file)
    return yaml_data


def check_benchmark(value: float, condition: str, benchmark: float) -> bool:
    """Check benchmark met.

    Args:
        value (float): Metric Value.
        condition (str): Condition to check.
        benchmark (float): Benchmark to meet

    Returns:
        bool: If benchmark was met.
    """
    if condition == ">":
        if value > benchmark:
            return True
    elif condition == ">=":
        if value >= benchmark:
            return True
    elif condition == "<=":
        if value <= benchmark:
            return True
    elif condition == "<":
        if value < benchmark:
            return True
    else:
        logger.error(f"Invalid condition {condition} given")
    return False


def check_prior_model_accuracy(model_name: str, current_accuracy: float) -> bool:
    """Compare against prior model.

    Args:
        model_name (str): Name of model to compare to.
        current_accuracy (float): Current model accuracy

    Returns:
        bool: If current model is more accurate.
    """
    run = Run.get_context()
    ws = run.experiment.workspace

    model_accuracies: list[float] = [
        float(m.properties.get("accuracy", 0.0))
        for m in Model.list(name=model_name, workspace=ws, latest=True)
    ]
    for accuracy in model_accuracies:
        if current_accuracy < accuracy:
            return False

    return True


def run_benchmarking(score_report: dict, benchmarks: list[dict]) -> bool:
    """Run model benchmarking.

    Args:
        score_report (dict): Scoring report.
        benchmarks (list[dict]): List of benchmarks to check.
    """
    has_error = False
    for benchmark in benchmarks:
        name = benchmark["metric"]
        condition = benchmark["condition"]
        benchmark = benchmark["benchmark"]

        value = score_report.get(name)

        if not value:
            logging.error(f"Error! Metric {name} not included in scoring report!")
            continue

        msg = f"Benchmark({name}) did not meet benchmark! {value} {condition} {benchmark} is false!"

        logging.info(f"Checking benchmark {name}")

        if not check_benchmark(value, condition, benchmark):
            logging.error(msg)
            has_error = True

    if has_error:
        return False

    logger.info("All benchmarks met!")
    return True


if __name__ == "__main__":
    args = parse_args()

    benchmark_report_path = Path(args.benchmark_report_folder) / "benchmark.json"
    score_report = parse_json_file(Path(args.score_report_folder) / "score_report.json")

    # Get configurations
    cfg = parse_yaml_file(args.model_config)
    logging_cfg = cfg["logging"]
    benchmark_cfg = cfg["benchmark"]
    mlflow_cfg = cfg["mlflow"]

    # Configure console logging.
    logging.config.dictConfig(logging_cfg)

    # Configure MLFlow
    mlflow.init_run(
        command_line_args=args,
        run_tags=run_tags,
        job_config=benchmark_cfg,
        mlflow_config=mlflow_cfg,
    )

    benchmarks_met = run_benchmarking(score_report, benchmark_cfg["conditions"])
    best_accuracy = check_prior_model_accuracy(
        benchmark_cfg["model_compare_name"], float(score_report.get("accuracy", 0.0))
    )

    benchmark_report = {
        "benchmarks_met": benchmarks_met,
        "best_accuracy": best_accuracy,
    }

    with open(benchmark_report_path, "w") as file:
        json.dump(benchmark_report, file, indent=4)

    mlflow.set_propagated_tags(benchmark_report)
