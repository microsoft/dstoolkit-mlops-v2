"""This module provides the functionality for initializing and running a machine learning model."""
import os
import logging
import json
import numpy
import joblib
import traceback
import sys


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def init():
    """
    Initialize the service instance on startup.

    You can write the logic here to perform init operations like caching the model in memory.
    """
    _setup_logging()
    global model
    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "model", "model.pkl")

    try:
        # deserialize the model file back into a sklearn model
        model = joblib.load(model_path)
        logging.info("Init complete")
    except Exception:
        logging.error("Exception during init(): %s", traceback.format_exc())
        try:
            with open("/tmp/score_init_traceback.log", "w") as fh:
                fh.write(traceback.format_exc())
        except Exception:
            logging.warning("Unable to write init traceback to /tmp/score_init_traceback.log")
        raise


def run(raw_data):
    """
    Execure inferencing logic on a request.

    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back.
    """
    logging.info("model 1: request received")
    try:
        data = json.loads(raw_data)["data"]
        data = numpy.array(data)

        result = model.predict(data)

        logging.info("Request processed")
        return result.tolist()
    except Exception:
        logging.error("Exception during run(): %s", traceback.format_exc())
        try:
            with open("/tmp/score_run_traceback.log", "w") as fh:
                fh.write(traceback.format_exc())
        except Exception:
            logging.warning("Unable to write run traceback to /tmp/score_run_traceback.log")
        raise
