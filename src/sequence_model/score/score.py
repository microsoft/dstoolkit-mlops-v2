"""
Sequence Model Scoring Module.

This module is used to score the predictions made by a trained n-gram model. It loads the model configuration,
predictions, and computes the accuracy of the predictions. The results are saved to a specified output folder.

Imports:
    - argparse: For parsing command-line arguments.
    - pathlib: For handling file paths.
    - json: For loading and saving JSON data.
    - logging: For logging information.
    - numpy: For numerical operations.
    - tqdm: For displaying progress bars.
    - yaml: For loading configuration files.
    - mlflow: For managing MLflow runs.

Attributes:
    logger (logging.Logger): Logger for the module.
    run_tags (dict): Tags for the MLflow run.
    current_run_id (str): Current MLflow run ID.
    parent_run_id (str): Parent MLflow run ID.

Command-line Arguments:
    --predictions_folder (str): Path to output artifacts from the predict step.
    --score_report_folder (str): Path to save the score report of the model's predictions on test data.
    --model_config (str): Path to the model configuration file.

Example:
    To run the module, use the following command:
    python -m src.sequence_model.score.score --predictions_folder <path_to_predictions>
    --score_report_folder <path_to_save_score_report> --model_config <path_to_model_config>
"""
import argparse
import pathlib
import json
import logging
import numpy as np
from tqdm import tqdm
import yaml
import src.sequence_model.common.mlflow_ext as mlflow

logger = logging.getLogger(__name__)

run_tags = {"model": "sequence_model", "step": "score"}
current_run_id: str = None
parent_run_id: str = None

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Sequence Model")

    parser.add_argument(
        "--predictions_folder",
        type=str,
        required=True,
        default=None,
        help="Path to output artifacts from predict step",
    )

    parser.add_argument(
        "--score_report_folder",
        type=str,
        required=True,
        default=None,
        help="Path to score report of model's predictions on test data",
    )

    parser.add_argument(
        "--model_config",
        type=str,
        required=True,
        default=None,
        help="Model configuration file",
    )

    args = parser.parse_args()

    # Load model yaml configuration
    cfg = yaml.safe_load(open(args.model_config))

    logging_cfg = cfg["logging"]
    model_cfg = cfg["model"]
    score_cfg = cfg["score"]
    mlflow_cfg = cfg["mlflow"]

    # Configure console logging.
    logging.config.dictConfig(logging_cfg)

    # Configure MLFlow
    _, parent_id = mlflow.init_run(
        args,
        run_tags,
        job_config=score_cfg,
        mlflow_config=mlflow_cfg,
    )

    max_prior_token_length = model_cfg["max_prior_token_length"]
    num_preds = score_cfg["num_preds"]

    assert (
        num_preds <= model_cfg["max_top_n"]
    ), f"Only {model_cfg['max_top_n']} predictions exist in file but {num_preds}" \
        "requested to be used to compute accuracy."

    # I/O
    score_report_root = pathlib.Path(args.score_report_folder)
    pathlib.Path(score_report_root).mkdir(exist_ok=True)

    # Input paths
    pred_name = "predictions.npy"
    pred_path = pathlib.Path(args.predictions_folder, pred_name)

    # Output paths
    score_path = pathlib.Path(score_report_root, "score_report.json")

    # Load predictions
    logger.info("Load predictions.")
    preds = np.load(pred_path)

    logger.info(
        f"Score predictions. Compute if ground truth exists in top {num_preds} results."
    )

    # Score predictions
    total_correct = 0
    for col_index in tqdm(
        range(max_prior_token_length, preds.shape[1]), desc="Scoring predictions..."
    ):
        col = preds[:, col_index]
        if col[0] in col[1:]:
            total_correct += 1

    acc = total_correct / (preds.shape[1] - max_prior_token_length)
    print("Acc:", acc)

    model_score = {
        "Accuracy": acc,
        "Num. predictions utilized": num_preds,
        "Max num predictions utilizable": model_cfg["max_top_n"],
    }

    with open(score_path, "w") as json_file:
        json.dump(model_score, json_file, indent=4)

    # Log Scoring output metrics
    mlflow.log_propagated_metrics(metrics=model_score, parent_run_id=parent_id)
