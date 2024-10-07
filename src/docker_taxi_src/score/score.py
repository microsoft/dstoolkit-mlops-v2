"""
This module provides functionality for scoring a machine learning model.

It allows users to load a trained model and a dataset containing actual and predicted values,
then evaluates the model's performance by calculating metrics such as Mean Squared Error (MSE)
and the Coefficient of Determination (R^2). The module also supports logging these metrics
using MLflow and outputs a score report.
"""
import argparse
import pandas as pd
import os
from pathlib import Path
import pickle
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import json


def main(predictions, model, score_report):
    """
    Load the test data and model, and write the results of the model scoring.

    Parameters:
    predictions (str): Path to the predictions.
    model (str): Path to the model.
    score_report (str): Path to the score report.

    Returns:
    None
    """
    print("hello scoring world...")

    lines = [
        f"Model path: {model}",
        f"Predictions path: {predictions}",
        f"Scoring output path: {score_report}",
    ]

    for line in lines:
        print(line)

    # Load the test data with predicted values

    print("mounted_path files: ")
    arr = os.listdir(predictions)

    print(arr)
    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        input_df = pd.read_csv((Path(predictions) / filename))
        df_list.append(input_df)

    test_data = df_list[0]

    # Load the model from input port
    model = pickle.load(open((Path(model) / "model.sav"), "rb"))
    write_results(model, predictions, test_data, score_report)


# Print the results of scoring the predictions against actual values in the test data
def write_results(model, predictions, test_data, score_report):
    """
    Calculate and log the model's mean squared error and coefficient of determination.

    Parameters:
    model (sklearn model): The trained model.
    predictions (DataFrame): The model's predictions.
    test_data (DataFrame): The test data.
    score_report (str): Path to the score report.

    Returns:
    None
    """
    # The coefficients
    print("Coefficients: \n", model.coef_)

    actuals = test_data["actual_cost"]
    predictions = test_data["predicted_cost"]

    mse = mean_squared_error(actuals, predictions)
    r2 = r2_score(actuals, predictions)

    mlflow.log_metric("scoring_mse", mse)
    mlflow.log_metric("scoring_r2", r2)

    # The mean squared error
    print("Mean squared error: %.2f" % mse)
    # The coefficient of determination: 1 is perfect prediction
    print("Coefficient of determination: %.2f" % r2)
    print("Model: ", model)

    # Print score report to a text file
    model_score = {
        "mse": mean_squared_error(actuals, predictions),
        "coff": str(model.coef_),
        "cod": r2_score(actuals, predictions),
    }
    with open((Path(score_report) / "score.txt"), "w") as json_file:
        json.dump(model_score, json_file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("score")
    parser.add_argument(
        "--predictions", type=str, help="Path of predictions and actual data"
    )
    parser.add_argument("--model", type=str, help="Path to model")
    parser.add_argument("--score_report", type=str, help="Path to score report")

    args = parser.parse_args()

    predictions = args.predictions
    model = args.model
    score_report = args.score_report

    main(predictions, model, score_report)
