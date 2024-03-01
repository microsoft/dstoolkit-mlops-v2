import argparse
from pathlib import Path
import os
import pandas as pd


def main(clean_data,transformed_data):
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
        with open(os.path.join(clean_data, filename),"r") :
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
    final_df = combined_df
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
