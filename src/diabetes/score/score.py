import argparse
import pandas as pd
import os
from pathlib import Path
import pickle
# from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import json

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

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
            input_df = pd.read_csv((Path(predictions) / filename))
            df_list.append(input_df)

    test_data = df_list[0]

    # Load the model from input port
    model = pickle.load(open((Path(model) / "model.sav"), "rb"))
    write_results(model, predictions, test_data, score_report)

# Print the results of scoring the predictions against actual values in the test data

def write_results(model, predictions, test_data, score_report):
    # The coefficients

    actuals = test_data["actual_outcome"]
    predictions = test_data["predicted_outcome"]
    # mse = mean_squared_error(actuals, predictions)
    # r2 = r2_score(actuals, predictions)

    # Compute classification metrics
    accuracy = accuracy_score(actuals, predictions)
    precision = precision_score(actuals, predictions)
    recall = recall_score(actuals, predictions)
    f1 = f1_score(actuals, predictions)

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)

    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1", f1)
                      
    # The mean squared error
    # print("Mean squared error: %.2f" % mse)
    # # The coefficient of determination: 1 is perfect prediction
    # print("Coefficient of determination: %.2f" % r2)
    print("Model: ", model)

    # Print score report to a text file
    model_score = {
        "accuracy": accuracy,
        "precision": precision ,
        "recall": recall ,
        "f1": f1
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
