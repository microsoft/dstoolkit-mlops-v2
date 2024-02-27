"""This module provides the functionality for initializing and running a machine learning model."""
import os
import logging
import json
import numpy
import joblib
import pandas as pd
from typing import List


def init():
    """
    Initialize the service instance on startup.

    You can write the logic here to perform init operations like caching the model in memory.
    """
    global model

    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "model", "model.pkl")

    # deserialize the model file back into a sklearn model
    model = joblib.load(model_path)
    logging.info("Init complete")


def run(mini_batch: List[str]) -> pd.DataFrame:
    """
    Execure inferencing logic on a request.

    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back.
    """
    results = []

    logging.info("model 1: request received")

    for raw_data in mini_batch:
        #data = json.loads(raw_data)["data"]
        #data = numpy.array(data)

        #result = model.predict(data)

        #results.append(result.tolist())

        results.append("Item has been processed")
        logging.info(raw_data)

        logging.info("Item has been proccessed")

    return pd.DataFrame(results)
