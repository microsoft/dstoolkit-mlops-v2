"""This module provides the functionality for initializing and running a machine learning model."""
import os
import logging
import json
import numpy
import joblib


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


def run(raw_data):
    """
    Execure inferencing logic on a request.

    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back.
    """
    logging.info("model 1: request received")
    data = json.loads(raw_data)["data"]
    data = numpy.array(data)

    result = model.predict(data)

    logging.info("Request processed")
    return result.tolist()
