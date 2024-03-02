import os
import logging
import json
import numpy
import joblib


def init():
    """
    This function is called when the container is initialized/started, typically after create/update of the deployment.
    You can write the logic here to perform init operations like caching the model in memory
    """
    global model

    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "model", "model.pkl")

    # deserialize the model file back into a sklearn model
    model = joblib.load(model_path)
    logging.info("Init complete")
    logging.info(os.environ['key2'])


def run(raw_data):
    """
    This function is called for every invocation of the endpoint to perform the actual scoring/prediction.
    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back
    """
    # current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # folder_path = f"{os.environ['MODEL_LOG_PATH']}{os.environ['MODEL_NAME']}/{current_time}"
    # if not os.path.exists(folder_path):
    #    os.makedirs(folder_path)
    # csv_input_path = f"{folder_path}/input.csv"
    # csv_output_path = f"{folder_path}/output.csv"
    logging.info("model 1: request received")
    data = json.loads(raw_data)["data"]
    data = numpy.array(data)
    # numpy.savetxt(csv_input_path, data, delimiter=",")

    result = model.predict(data)

    # numpy.savetxt(csv_output_path, result, delimiter=",")
    logging.info("Request processed")
    return result.tolist()
