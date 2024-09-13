"""This module provides the functionality for initializing and running a machine learning model."""
import os
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
    print("Init complete")


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
        data = pd.read_csv(raw_data)

        result = model.predict(data.to_numpy())
        print(f"predicted results: {result}")

        print("Item has been proccessed")

        # You need to implement a better way to combine results from the model depends on your desired output
        results.append("Item has been processed")

    return pd.DataFrame(results)
