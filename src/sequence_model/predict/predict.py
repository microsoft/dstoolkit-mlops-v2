"""
Sequence Model Prediction Module.

This module is used to predict the next tokens in a sequence using a trained n-gram model.
It loads the model and tokenizer, tokenizes the test data, and makes predictions based on
the provided prior tokens. The predictions are saved to a specified
output folder.

Imports:
    - argparse: For parsing command-line arguments.
    - logging: For logging information.
    - pickle: For loading and saving data.
    - pathlib: For handling file paths.
    - numpy: For numerical operations.
    - tqdm: For displaying progress bars.
    - yaml: For loading configuration files.
    - Tokenizer: For tokenizing the input data.
    - NgramModel: For the n-gram model.
    - mlflow: For managing MLflow runs.

Attributes:
    logger (logging.Logger): Logger for the module.
    run_tags (dict): Tags for the MLflow run.
    current_run_id (str): Current MLflow run ID.
    parent_run_id (str): Parent MLflow run ID.

Command-line Arguments:
    --dataset_folder (str): Path hosting test data.
    --model_artifacts (str): Path to model artifacts from the training step.
    --predictions_folder (str): Path to save the serialized set of model predictions on test data.
    --model_config (str): Path to the model configuration file.

Example:
    To run the module, use the following command:
    python -m src.sequence_model.predict.predict --dataset_folder <path_to_test_data> --model_artifacts
    <path_to_model_artifacts> --predictions_folder <path_to_save_predictions>
    --model_config <path_to_model_config>
"""
import argparse
import logging
import pickle
import pathlib
import numpy as np
from tqdm import tqdm
import yaml
from src.sequence_model.common.tokenizer import Tokenizer
from src.sequence_model.common.seq_model import NgramModel
import src.sequence_model.common.mlflow_ext as mlflow

logger = logging.getLogger(__name__)

run_tags = {"model": "sequence_model", "step": "predict"}
current_run_id: str = None
parent_run_id: str = None

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Sequence Model")

    parser.add_argument(
        "--dataset_folder",
        type=str,
        required=True,
        default=None,
        help="Path hosting test data",
    )

    parser.add_argument(
        "--model_artifacts",
        type=str,
        required=True,
        default=None,
        help="Path to model artifacts from train step",
    )

    parser.add_argument(
        "--predictions_folder",
        type=str,
        required=True,
        default=None,
        help="Path to serialized set of model predictions on test data",
    )

    parser.add_argument(
        "--model_config",
        type=str,
        required=True,
        default=None,
        help="model configuration",
    )

    args = parser.parse_args()

    # Load model yaml configuration
    cfg = yaml.safe_load(open(args.model_config))

    logging_cfg = cfg["logging"]
    model_cfg = cfg["model"]
    mlflow_cfg = cfg["mlflow"]

    # Configure logging
    logging.config.dictConfig(logging_cfg)

    # Configure mlflow
    _, parent_run_id = mlflow.init_run(
        args,
        run_tags,
        job_config=(
            model_cfg  # Concatenate dictionaries of further configuration here
        ),
        mlflow_config=mlflow_cfg,
    )

    # I/O operations
    model_artifacts = pathlib.Path(args.model_artifacts)
    model_root = pathlib.Path(model_artifacts, "model")
    tokenizer_root = pathlib.Path(model_artifacts, "tokenizer")

    # Input paths
    model_path = pathlib.Path(model_root, "model_dict.pkl")
    tokenizer_path = pathlib.Path(tokenizer_root, "tokenizer.json")
    test_data_path = pathlib.Path(args.dataset_folder, "test.pkl")

    # Output paths
    pathlib.Path(args.predictions_folder).mkdir(exist_ok=True)
    predictions_path = pathlib.Path(args.predictions_folder, "predictions")

    logger.info(f"run_id :::: {current_run_id}")

    # Load tokenizer
    logger.info("Load tokenizer.")
    tokenizer = Tokenizer()
    tokenizer.load(path=tokenizer_path)
    logger.info(f"Vocabularly size: {tokenizer.vocab_size}.")

    # Load model
    logger.info("Load model.")
    model = NgramModel(
        max_prior_token_length=model_cfg["max_prior_token_length"],
        max_top_n=model_cfg["max_top_n"],
    )
    model.load(model_path)

    # Load data
    logger.info("Load data.")
    with open(test_data_path, "rb") as f:
        test_data = pickle.load(f)

    # Tokenize data
    logger.info("Tokenizing test data.")
    tokenized_data = tokenizer.tokenize(corpus=test_data)

    # Predict
    # A sample of the predictions
    # |  129,  8911,  682, 20116,    10,     5| <- Original data
    # |   -1,    -1,   -1,   112,    10, 13412| <- Best prediction
    # |   -1,    -1,   -1, 20116, 12414, 43212| <- Second best
    # |   -1,    -1,   -1,  5623, 19710, 45061| <- Third best
    # Top row of predictions is original data
    # Every row beyond the first is the n'th best prediction given the history
    # For columns where entries are None, no prediction is made.
    # For for ngram length of 3, the first 3 columns will have no prediction.

    preds = np.zeros((model_cfg["max_top_n"] + 1, len(tokenized_data)), dtype=int)
    preds[0, :] = tokenized_data
    logger.info("Making predictions.")
    for ngram_index in tqdm(
        range(0, len(tokenized_data) - model_cfg["max_prior_token_length"]),
        desc="Iterating over test file...",
    ):
        # Get current ngram
        cur_ngram = tuple(
            tokenized_data[
                ngram_index: ngram_index + model_cfg["max_prior_token_length"]
            ]
        )

        # Make a prediction
        cur_pred = model.predict(
            prior_tokens=cur_ngram, top_n=model_cfg["max_top_n"]
        )  # Always make max preds
        # Append -1 tokens when predictions is subset of max_top_n to indicate no prediction
        if len(cur_pred) < model_cfg["max_top_n"]:
            cur_pred = cur_pred + [-1] * (model_cfg["max_top_n"] - len(cur_pred))
        # Write pred to array
        preds[
            1: model_cfg["max_top_n"] + 1,
            ngram_index + model_cfg["max_prior_token_length"],
        ] = cur_pred

    # Save predictions
    np.save(predictions_path, preds)
