"""
This module is designed to train a machine learning model.

The module performs the following key steps:
1. Reading and combining data from specified training data files.
2. Splitting the combined data into training and testing datasets.
3. Training a Linear Regression model using the training dataset.
4. Using MLflow for logging and tracking experiments.
5. Saving the trained model and its metadata to specified paths.
"""
import argparse
from pathlib import Path
import os
import pandas as pd
# from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
import mlflow
import json

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report


def main(training_data, test_data, model_output, model_metadata):
    """
    Read training data, split data and initiate training.

    Parameters:
      training_data (str): training data folder
      test_data (str): test data folder
      model_output (str): a folder to store model files
      model_metadata (str): a file to store information about thr model
    """
    print("Hello training world...")

    lines = [
        f"Training data path: {training_data}",
        f"Test data path: {test_data}",
        f"Model output path: {model_output}",
        f"Model metadata path: {model_metadata}",
    ]

    for line in lines:
        print(line)

    print("mounted_path files: ")
    arr = os.listdir(training_data)
    print(arr)

    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        with open(os.path.join(training_data, filename), "r"):
            input_df = pd.read_csv((Path(training_data) / filename))
            df_list.append(input_df)

    train_data = df_list[0]
    print(train_data.columns)

    trainx, testx, trainy, testy = split(train_data)
    write_test_data(testx, testy)
    train_model(trainx, trainy)


def split(train_data):
    """
    Split the input data into training and testing sets.

    Parameters:
    train_data (DataFrame): The input data.

    Returns:
    trainX (DataFrame): The training data.
    testX (DataFrame): The testing data.
    trainy (Series): The training labels.
    testy (Series): The testing labels.
    """
    # Split the data into input(X) and output(y)

    y = train_data["cost"]
    x = train_data[
        [
            "pregnancies",
            "glucose",
            "bloodpressure",
            "skinthickness",
            "insulin",
            "bmi",
            "diabetespedigreefunction",
            "age",
        ]
    ]

    # Split the data into train and test sets
    trainx, testx, trainy, testy = train_test_split(
        x, y, test_size=0.3, random_state=42
    )
    print(trainx.shape)
    print(trainx.columns)

    return trainx, testx, trainy, testy


def train_model(trainx, trainy):
    """
    Train a Linear Regression model and save the model and its metadata.

    Parameters:
    trainX (DataFrame): The training data.
    trainy (Series): The training labels.

    Returns:
    None
    """
    mlflow.autolog()
    # Train a Linear Regression Model with the train set
    with mlflow.start_run() as run:
        # model = LinearRegression().fit(trainX, trainy)

        model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1)
        # model = xgb.XGBClassifier(objective="binary:logistic", random_state=42)
        # model = SVC(kernel='linear', C=1.0)
        model.fit(trainx, trainy)

        # print(model.score(trainX, trainy))

        y_pred = model.predict(trainx)

        print(y_pred)
        print(classification_report(trainy, y_pred))
        # cm = confusion_matrix(trainX, y_pred)
        # print(cm)

        # Output the model, metadata and test data
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/model"
        model_data = {"run_id": run.info.run_id, "run_uri": model_uri}
        with open(args.model_metadata, "w") as json_file:
            json.dump(model_data, json_file, indent=4)

        pickle.dump(model, open((Path(args.model_output) / "model.sav"), "wb"))


def write_test_data(testx, testy):
    """
    Write the testing data to a CSV file.

    Parameters:
    testX (DataFrame): The testing data.
    testy (Series): The testing labels.

    Returns:
    None
    """
    testx["outcome"] = testy
    print(testx.shape)
    testx.to_csv((Path(args.test_data) / "test_data.csv"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("train")
    parser.add_argument("--training_data", type=str, help="Path to training data")
    parser.add_argument("--test_data", type=str, help="Path to test data")
    parser.add_argument("--model_output", type=str, help="Path of output model")
    parser.add_argument("--model_metadata", type=str, help="Path of model metadata")

    args = parser.parse_args()

    training_data = args.training_data
    test_data = args.test_data
    model_output = args.model_output
    model_metadata = args.model_metadata

    main(training_data, test_data, model_output, model_metadata)
