"""
This module is responsible for transforming pre-processed data for the London Taxi dataset.

The module includes a main function that orchestrates the reading of cleaned data,
performs further transformations, and outputs the transformed data for model training.
The transformations involve filtering out geographical coordinates outside the city borders,
normalizing data types, splitting datetime fields into more granular components, and
filtering out outliers in the dataset.
"""

import argparse
from pathlib import Path
import os
import pandas as pd
import numpy as np


def main(clean_data, transformed_data):
    """
    Initiate transformation and save results into csv file.

    Parameters:
      clean_data (str): a folder to store results
      transformed_data (DataFrame): an initial data frame for transformation
    """
    lines = [
        f"Clean data path: {clean_data}",
        f"Transformed data output path: {transformed_data}",
    ]

    for line in lines:
        print(line)

    print("mounted_path files: ")
    arr = os.listdir(clean_data)
    print(arr)

    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        input_df = pd.read_csv((Path(clean_data) / filename))
        df_list.append(input_df)

    # Transform the data
    combined_df = df_list[1]
    final_df = transform_data(combined_df)

    # Output data
    final_df.to_csv((Path(args.transformed_data) / "transformed_data.csv"))


# These functions filter out coordinates for locations that are outside the city border.

# Filter out coordinates for locations that are outside the city border.
# Chain the column filter commands within the filter() function
# and define the minimum and maximum bounds for each field


def transform_data(combined_df):
    """
    Transform a dataframe to prepare it for training.

    The method is implementing data cleaning and normalization

    Parameters:
      combined_df (pandas.DataFrame): incoming data frame

    Returns:
        DataFrame: transformed data frame
    """
    combined_df = combined_df.astype(
        {
            "pickup_longitude": "float64",
            "pickup_latitude": "float64",
            "dropoff_longitude": "float64",
            "dropoff_latitude": "float64",
        }
    )

    latlong_filtered_df = combined_df[
        (combined_df.pickup_longitude <= -73.72)
        & (combined_df.pickup_longitude >= -74.09)
        & (combined_df.pickup_latitude <= 40.88)
        & (combined_df.pickup_latitude >= 40.53)
        & (combined_df.dropoff_longitude <= -73.72)
        & (combined_df.dropoff_longitude >= -74.72)
        & (combined_df.dropoff_latitude <= 40.88)
        & (combined_df.dropoff_latitude >= 40.53)
    ]

    latlong_filtered_df.reset_index(inplace=True, drop=True)

    # These functions replace undefined values and rename to use meaningful names.
    replaced_stfor_vals_df = latlong_filtered_df.replace(
        {"store_forward": "0"}, {"store_forward": "N"}
    ).fillna({"store_forward": "N"})

    replaced_distance_vals_df = replaced_stfor_vals_df.replace(
        {"distance": ".00"}, {"distance": 0}
    ).fillna({"distance": 0})

    normalized_df = replaced_distance_vals_df.astype({"distance": "float64"})

    # These functions transform the renamed data to be used finally for training.

    # Split the pickup and dropoff date further into the day of the week, day of the month, and month values.
    # To get the day of the week value, use the derive_column_by_example() function.
    # The function takes an array parameter of example objects that define the input data,
    # and the preferred output. The function automatically determines your preferred transformation.
    # For the pickup and dropoff time columns, split the time into the hour, minute, and second by using
    # the split_column_by_example() function with no example parameter. After you generate the new features,
    # use the drop_columns() function to delete the original fields as the newly generated features are preferred.
    # Rename the rest of the fields to use meaningful descriptions.

    temp = pd.DatetimeIndex(normalized_df["pickup_datetime"], dtype="datetime64[ns]")
    normalized_df["pickup_date"] = temp.date
    normalized_df["pickup_weekday"] = temp.dayofweek
    normalized_df["pickup_month"] = temp.month
    normalized_df["pickup_monthday"] = temp.day
    normalized_df["pickup_time"] = temp.time
    normalized_df["pickup_hour"] = temp.hour
    normalized_df["pickup_minute"] = temp.minute
    normalized_df["pickup_second"] = temp.second

    temp = pd.DatetimeIndex(normalized_df["dropoff_datetime"], dtype="datetime64[ns]")
    normalized_df["dropoff_date"] = temp.date
    normalized_df["dropoff_weekday"] = temp.dayofweek
    normalized_df["dropoff_month"] = temp.month
    normalized_df["dropoff_monthday"] = temp.day
    normalized_df["dropoff_time"] = temp.time
    normalized_df["dropoff_hour"] = temp.hour
    normalized_df["dropoff_minute"] = temp.minute
    normalized_df["dropoff_second"] = temp.second

    del normalized_df["pickup_datetime"]
    del normalized_df["dropoff_datetime"]

    normalized_df.reset_index(inplace=True, drop=True)

    print(normalized_df.head)
    print(normalized_df.dtypes)

    # Drop the pickup_date, dropoff_date, pickup_time, dropoff_time columns because they're
    # no longer needed (granular time features like hour,
    # minute and second are more useful for model training).
    del normalized_df["pickup_date"]
    del normalized_df["dropoff_date"]
    del normalized_df["pickup_time"]
    del normalized_df["dropoff_time"]

    # Change the store_forward column to binary values
    normalized_df["store_forward"] = np.where(
        (normalized_df.store_forward == "N"), 0, 1
    )

    # Before you package the dataset, run two final filters on the dataset.
    # To eliminate incorrectly captured data points,
    # filter the dataset on records where both the cost and distance variable values are greater than zero.
    # This step will significantly improve machine learning model accuracy,
    # because data points with a zero cost or distance represent major outliers that throw off prediction accuracy.

    final_df = normalized_df[(normalized_df.distance > 0) & (normalized_df.cost > 0)]
    final_df.reset_index(inplace=True, drop=True)
    print(final_df.head)

    return final_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser("transform")
    parser.add_argument("--clean_data", type=str, help="Path to prepped data")
    parser.add_argument("--transformed_data", type=str, help="Path of output data")

    args = parser.parse_args()

    clean_data = args.clean_data
    transformed_data = args.transformed_data
    main(clean_data, transformed_data)