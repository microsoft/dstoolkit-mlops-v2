"""This module provides the functionality for initializing and running a machine learning model."""

import os
import logging
import json
import yaml
from seq_model import NgramModel
from tokenizer import Tokenizer


def init():
    """
    Initialize the service instance on startup.

    You can write the logic here to perform init operations like caching the model in memory.
    """
    global model
    global tokenizer
    global model_cfg

    model_path = os.path.join(
        os.getenv("AZUREML_MODEL_DIR"), "model_registration", "model", "model_dict.pkl"
    )
    tokenizer_path = os.path.join(
        os.getenv("AZUREML_MODEL_DIR"),
        "model_registration",
        "tokenizer",
        "tokenizer.json",
    )
    model_cfg_path = "model_config.yml"

    cfg = yaml.safe_load(open(model_cfg_path))
    model_cfg = cfg['model']

    # deserialize the model
    model = NgramModel(
        max_prior_token_length=model_cfg["max_prior_token_length"],
        max_top_n=model_cfg["max_top_n"],
    )
    model.load(model_path)

    # deserialize the tokenizer
    tokenizer = Tokenizer.load(tokenizer_path)

    logging.info("Init complete")


def run(raw_data):
    """
    Execute inferencing logic on a request.

    In the example we extract the data from the json input and call the model's predict()
    method and return the result back.
    """
    logging.info("model 1: request received")
    data = json.loads(raw_data)["data"]

    assert (
        len(data) <= model_cfg["max_prior_token_length"]
    ), f"Only {model_cfg['max_prior_token_length']} prior words can \
    be used for next prediction but {len(data)} words exist in request."

    # Encode data
    tokenized_data = tuple(tokenizer.enc(words=data))

    result = model.predict(tokenized_data)

    # Decode result
    preds = tokenizer.dec(tokens=result)

    logging.info("Request processed")

    return preds
