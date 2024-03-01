"""
This module is designed to preprocess taxi data for the Azure Machine Learning NYC Taxi tutorial.

It includes functions for reading raw taxi data (both green and yellow taxi data),
cleaning it, and transforming it into a format suitable for machine learning modeling.
The module focuses on selecting useful columns, renaming them as per tutorial specifications,
and concatenating the green and yellow taxi data into a single dataset.
"""

import argparse
from pathlib import Path
import os
import pandas as pd


def main(raw_data, prep_data):
    """
    Read existing csv files and invoke preprocessing step.

    Parameters:
      raw_data (str): a folder to read csv files
      prep_data (str): a folder for preprocessed data
    """
    print("hello training world...")

    lines = [
        f"Raw data path: {raw_data}",
        f"Data output path: {prep_data}",
    ]

    for line in lines:
        print(line)

    print("mounted_path files: ")
    arr = os.listdir(raw_data)
    print(arr)

    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        with open(os.path.join(raw_data, filename), "r"):
            input_df = pd.read_csv((Path(raw_data) / filename))
            df_list.append(input_df)

    # Prep the green and yellow taxi data
    # green_data = df_list[0]
    # yellow_data = df_list[1]
    data = df_list[0]

    data_prep(data)


def data_prep(data):
    """
    Define useful columns needed for the Azure Machine Learning NYC Taxi tutorial.

    Output columns are Pregnancies	Glucose	BloodPressure	SkinThickness	Insulin	BMI	DiabetesPedigreeFunction	Age	Outcome

    Parameters:
      data (pandas.DataFrame): raw data
    """
    useful_columns = str(
        [
            "pregnancies",
            "glucose",
            "bloodpressure",
            "skinthickness",
            "insulin",
            "bmi",
            "diabetespedigreefunction",
            "age",
            "outcome",
        ]
    ).replace(",", ";")
    print(useful_columns)

    # Rename columns as per Azure Machine Learning NYC Taxi tutorial
    data_columns = str(
        {
            "Pregnancies": "pregnancies",
            "Glucose": "glucose",
            "BloodPressure": "bloodpressure",
            "SkinThickness": "skinthickness",
            "Insulin": "insulin",
            "BMI": "bmi",
            "DiabetesPedigreeFunction": "diabetespedigreefunction",
            "Age": "age",
            "Outcome": "outcome",
        }
    ).replace(",", ";")

    print("data_columns: " + data_columns)

    data_clean = cleansedata(data, data_columns, useful_columns)

    # # Append yellow data to green data
    # combined_df = pd.concat([green_data_clean, yellow_data_clean], ignore_index=True)
    # #combined_df = green_data_clean.append(yellow_data_clean, ignore_index=True)

    combined_df = data_clean
    combined_df.reset_index(inplace=True, drop=True)

    # output_green = data_clean.to_csv(
    #     os.path.join(prep_data, "clean_data.csv")
    # )
    # output_yellow = yellow_data_clean.to_csv(
    #     os.path.join(prep_data, "yellow_prep_data.csv")
    # )
    # merged_data = combined_df.to_csv(os.path.join(prep_data, "merged_data.csv"))

    print("Finish")

# These functions ensure that null data is removed from the dataset,
# which will help increase machine learning model accuracy.


def get_dict(dict_str):
    """
    Ensure that null data is removed from the dataset to increase machine learning model accuracy.

    Parameters:
      dict_str (Dictionary): a string with separated elements

    Returns:
      Dictionary: an updated dictionary
    """
    pairs = dict_str.strip("{}").split(";")
    new_dict = {}
    for pair in pairs:
        print(pair)
        key, value = pair.strip().split(":")
        new_dict[key.strip().strip("'")] = value.strip().strip("'")
    return new_dict


def cleansedata(data, columns, useful_columns):
    """
    Clean dataset removing NA values.

    Parameters:
      data (pandas.DataFrame): initial data
      columns (str): a list of columns in initial dataset
      useful_columns (str): columns to retain

    Returns:
      DataFrame: an updated data set
    """
    useful_columns = [
        s.strip().strip("'") for s in useful_columns.strip("[]").split(";")
    ]
    new_columns = get_dict(columns)

    new_df = (data.dropna(how="all").rename(columns=new_columns))[useful_columns]

    new_df.reset_index(inplace=True, drop=True)
    return new_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw_data",
        type=str,
        default="../data/raw_data",
        help="Path to raw data",
    )
    parser.add_argument(
        "--prep_data", type=str, default="../data/prep_data", help="Path to prep data"
    )

    args = parser.parse_args()
    raw_data = args.raw_data
    prep_data = args.prep_data

    main(raw_data, prep_data)
