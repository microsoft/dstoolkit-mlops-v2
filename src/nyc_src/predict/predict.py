import argparse
import pandas as pd
import os
from pathlib import Path
from sklearn.linear_model import LinearRegression
import pickle


def main(model_input, test_data, prediction_path):
    lines = [
        f"Model path: {model_input}",
        f"Test data path: {test_data}",
        f"Predictions path: {prediction_path}",
    ]

    for line in lines:
        print(line)

    testX, testy = load_test_data(test_data)
    predict(testX, testy, model_input, prediction_path)


# Load and split the test data


def load_test_data(test_data):
    print("mounted_path files: ")
    arr = os.listdir(test_data)

    print(arr)
    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        with open(os.path.join(test_data, filename), "r") as handle:
            # print (handle.read())
            input_df = pd.read_csv((Path(test_data) / filename))
            df_list.append(input_df)

    test_data = df_list[0]
    testy = test_data["cost"]
    # testX = test_data.drop(['cost'], axis=1)
    testX = test_data[
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
    print(testX.shape)
    print(testX.columns)
    return testX, testy


def predict(testX, testy, model_input, prediction_path):
    # Load the model from input port
    model = pickle.load(open((Path(model_input) / "model.sav"), "rb"))

    # model = (Path(model_input) / 'model.txt').read_text()
    # print('Model: ', model)

    # Make predictions on testX data and record them in a column named predicted_cost
    predictions = model.predict(testX)
    testX["predicted_cost"] = predictions
    print(testX.shape)

    # Compare predictions to actuals (testy)
    output_data = pd.DataFrame(testX)
    output_data["actual_cost"] = testy

    # Save the output data with feature columns, predicted cost, and actual cost in csv file
    output_data = output_data.to_csv((Path(prediction_path) / "predictions.csv"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("predict")
    parser.add_argument("--model_input", type=str, help="Path of input model")
    parser.add_argument("--test_data", type=str, help="Path to test data")
    parser.add_argument("--predictions", type=str, help="Path of predictions")

    args = parser.parse_args()

    print("hello scoring world...")

    model_input = args.model_input
    test_data = args.test_data
    prediction_path = args.predictions
    main(model_input, test_data, prediction_path)
