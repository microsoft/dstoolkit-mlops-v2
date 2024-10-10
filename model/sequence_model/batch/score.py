"""This module provides the functionality for initializing and running a machine learning model."""

import os
import logging
import pandas as pd
from typing import List
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

    contents = os.listdir('.')
    for item in contents:
        print(item)

    cfg = yaml.safe_load(open(model_cfg_path))
    model_cfg = cfg['model']
    # deserialize the model
    model = NgramModel(
        max_prior_token_length=model_cfg["max_prior_token_length"],
        max_top_n=model_cfg["max_top_n"],
    )
    model.load(model_path)

    # deserialize the tokenizer
    tokenizer = Tokenizer()
    tokenizer.load(tokenizer_path)

    logging.info("Init complete")


def run(mini_batch: List[str]) -> pd.DataFrame:
    """
    Execure inferencing logic on a request.

    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back.
    """
    results = []

    print("Request received")

    for raw_data in mini_batch:
        print(f"File name: {raw_data}")
        with open("sequence_model.csv", "r") as f:
            for line in f:
                data = tuple(line.strip().split(" "))
                tokenized_data = tokenizer.enc(words=data)
                result = model.predict(tokenized_data)
                preds = tokenizer.dec(result)
                print("Input data:", line.strip())
                print("Possible choices for next word:", preds)

        print(f"File name: {raw_data} has been processed")

        # You need to implement a better way to combine results from the model depends on your desired output
        results.append(f"File name: {raw_data} has been processed")

    return pd.DataFrame(results)
