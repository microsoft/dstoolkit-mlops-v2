"""
This module processes and prepares taxi data for machine learning analysis.

The module includes functionalities for reading raw taxi data, cleaning it,
and transforming it into a format suitable for machine learning models. It specifically
handles green and yellow taxi data, applying predefined transformations and combining
the datasets. The output is saved as prepared data files for subsequent analysis.
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
        input_df = pd.read_csv((Path(raw_data) / filename))
        df_list.append(input_df)

    # Prep the green and yellow taxi data
    green_data = df_list[0]
    yellow_data = df_list[1]

    data_prep(green_data, yellow_data, prep_data)


def data_prep(green_data, yellow_data, prep_data):
    """
    Merge two data sets for different taxi vendors.

    The method maps columns in two data sets and remove distinct columns
     saving results as a csv file.

    Parameters:
      green_data (pandas.DataFrame): incoming data frame for green taxi
      yellow_data (pandas.DataFrame): incoming data frame for yellow taxi
      prep_data (str): a folder for preprocessed data
    """
    # Define useful columns needed for the Azure Machine Learning London Taxi tutorial
    useful_columns = str(
        [
            "cost",
            "distance",
            "dropoff_datetime",
            "dropoff_latitude",
            "dropoff_longitude",
            "passengers",
            "pickup_datetime",
            "pickup_latitude",
            "pickup_longitude",
            "store_forward",
            "vendor",
        ]
    ).replace(",", ";")
    print(useful_columns)

    # Rename columns as per Azure Machine Learning London Taxi tutorial
    green_columns = str(
        {
            "vendorID": "vendor",
            "lpepPickupDatetime": "pickup_datetime",
            "lpepDropoffDatetime": "dropoff_datetime",
            "storeAndFwdFlag": "store_forward",
            "pickupLongitude": "pickup_longitude",
            "pickupLatitude": "pickup_latitude",
            "dropoffLongitude": "dropoff_longitude",
            "dropoffLatitude": "dropoff_latitude",
            "passengerCount": "passengers",
            "fareAmount": "cost",
            "tripDistance": "distance",
        }
    ).replace(",", ";")

    yellow_columns = str(
        {
            "vendorID": "vendor",
            "tpepPickupDateTime": "pickup_datetime",
            "tpepDropoffDateTime": "dropoff_datetime",
            "storeAndFwdFlag": "store_forward",
            "startLon": "pickup_longitude",
            "startLat": "pickup_latitude",
            "endLon": "dropoff_longitude",
            "endLat": "dropoff_latitude",
            "passengerCount": "passengers",
            "fareAmount": "cost",
            "tripDistance": "distance",
        }
    ).replace(",", ";")

    print("green_columns: " + green_columns)
    print("yellow_columns: " + yellow_columns)

    green_data_clean = cleansedata(green_data, green_columns, useful_columns)
    yellow_data_clean = cleansedata(yellow_data, yellow_columns, useful_columns)

    # Append yellow data to green data
    combined_df = pd.concat([green_data_clean, yellow_data_clean], ignore_index=True)
    combined_df.reset_index(inplace=True, drop=True)

    green_data_clean.to_csv(os.path.join(prep_data, "green_prep_data.csv"))
    yellow_data_clean.to_csv(os.path.join(prep_data, "yellow_prep_data.csv"))
    combined_df.to_csv(os.path.join(prep_data, "merged_data.csv"))

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

    main(args.raw_data, args.prep_data)
