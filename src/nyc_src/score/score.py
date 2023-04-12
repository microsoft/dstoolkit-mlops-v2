import argparse
import pandas as pd
import os
from pathlib import Path
from sklearn.linear_model import LinearRegression
import pickle
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import json


def main(predictions, model, score_report):
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
        with open(os.path.join(predictions, filename), "r") as handle:
            # print (handle.read())
            input_df = pd.read_csv((Path(predictions) / filename))
            df_list.append(input_df)

    test_data = df_list[0]

    # Load the model from input port
    model = pickle.load(open((Path(model) / "model.sav"), "rb"))
    write_results(model, predictions, test_data, score_report)


# Print the results of scoring the predictions against actual values in the test data


def write_results(model, predictions, test_data, score_report):
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
