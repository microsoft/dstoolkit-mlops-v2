import argparse
from pathlib import Path
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
import mlflow
import json


def main(training_data, test_data, model_output, model_metadata):
    """
    Main function for training the model.

    Args:
        training_data (str): Path to the training data.
        test_data (str): Path to the test data.
        model_output (str): Path to save the trained model.
        model_metadata (str): Path to save the model metadata.

    Returns:
        None
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
        with open(os.path.join(training_data, filename), "r") as handle:
            input_df = pd.read_csv((Path(training_data) / filename))
            df_list.append(input_df)

    train_data = df_list[0]
    print(train_data.columns)

    trainX, testX, trainy, testy = split(train_data)
    write_test_data(testX, testy)
    train_model(trainX, trainy)


def split(train_data):
    """
    Split the data into train and test sets.

    Parameters:
    train_data (DataFrame): The input data containing features and target variable.

    Returns:
    trainX (DataFrame): The training data features.
    testX (DataFrame): The testing data features.
    trainy (Series): The training data target variable.
    testy (Series): The testing data target variable.
    """
    y = train_data["cost"]
    X = train_data[
        [
            "distance",
            "dropoff_latitude",
            "dropoff_longitude",
            "passengers",
            "pickup_latitude",
            "pickup_longitude",
            "store_forward",
            "vendor",
            "pickup_weekday",
            "pickup_month",
            "pickup_monthday",
            "pickup_hour",
            "pickup_minute",
            "pickup_second",
            "dropoff_weekday",
            "dropoff_month",
            "dropoff_monthday",
            "dropoff_hour",
            "dropoff_minute",
            "dropoff_second",
        ]
    ]

    trainX, testX, trainy, testy = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    print(trainX.shape)
    print(trainX.columns)

    return trainX, testX, trainy, testy


def train_model(trainX, trainy):
    """
    Train a Linear Regression Model with the given train set.

    Parameters:
    trainX (array-like): The input features for training the model.
    trainy (array-like): The target variable for training the model.

    Returns:
    None
    """
    mlflow.autolog()
    # Train a Linear Regression Model with the train set
    with mlflow.start_run() as run:
        model = LinearRegression().fit(trainX, trainy)
        print(model.score(trainX, trainy))

        # Output the model, metadata and test data
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/model"
        model_data = {"run_id": run.info.run_id, "run_uri": model_uri}
        with open(args.model_metadata, "w") as json_file:
            json.dump(model_data, json_file, indent=4)

        pickle.dump(model, open((Path(args.model_output) / "model.sav"), "wb"))


def write_test_data(testX, testy):
    """
    Write test data to a CSV file.

    Args:
        testX (pandas.DataFrame): The test features.
        testy (pandas.Series): The test labels.

    Returns:
        None
    """
    testX["cost"] = testy
    print(testX.shape)
    testX.to_csv((Path(args.test_data) / "test_data.csv"))


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
