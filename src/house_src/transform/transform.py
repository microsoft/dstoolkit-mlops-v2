import argparse
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import os
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsRegressor


def main(clean_data, transformed_data):
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
        with open(os.path.join(clean_data, filename), "r") as handle:
            input_df = pd.read_csv((Path(clean_data) / filename))

    # Transform the data
    final_df = transform_data(input_df)

    # Output data
    final_df.to_csv((Path(args.transformed_data) / "transformed_data.csv"))


# These functions filter out coordinates for locations that are outside the city border.

# Filter out coordinates for locations that are outside the city border.
# Chain the column filter commands within the filter() function
# and define the minimum and maximum bounds for each field

def transform_data(df):
    # Data Cleaning
    df.drop('Id',axis=1,inplace=True)
    df.MSSubClass=df.MSSubClass.astype('str')

    #filling the features which Na has meaning in it 
    cat_f_1=['Alley','BsmtQual','BsmtCond','BsmtExposure','BsmtFinType1','BsmtFinType2','FireplaceQu','GarageType','GarageFinish','GarageQual','GarageCond','PoolQC','Fence','MiscFeature']
    for column in cat_f_1:
        df[column] = df[column].fillna("None")
    df.select_dtypes('O').isnull().sum().sort_values(ascending=False)

    #filling the other cat features with the most frequent value
    cat_f_2=['MasVnrType','MSZoning','Functional','Utilities','SaleType','Exterior2nd','Exterior1st','Electrical' ,'KitchenQual']
    for column in cat_f_2:
        df[column] = df[column].fillna(df[column].mode()[0])
    df.select_dtypes('O').isnull().sum().sort_values(ascending=False).sum()

    # Handling numerical Missing Value
    num_f=['LotFrontage','MasVnrArea','BsmtFinSF1','BsmtFinSF2','BsmtUnfSF','TotalBsmtSF','BsmtFullBath','BsmtHalfBath','GarageYrBlt','GarageCars','GarageArea']
    for column in num_f:
        df[column] = df[column].fillna(df[column].mode()[0])
    df.select_dtypes('O').isnull().sum().sort_values(ascending=False).sum()
    clean_df = df
    
    # Feature Engineering
    #LotFrontage: Linear feet of street connected to property
    #LotArea: Lot size in square feet

    # we can combine the both features to get the total area of both 
    clean_df['TotalArea']=clean_df['LotFrontage']+clean_df['LotArea']

    #OverallQual: Rates the overall material and finish of the house
    #OverallCond: Rates the overall condition of the house

    clean_df['Total_Home_Quality'] = clean_df['OverallQual'] + clean_df['OverallCond']
    clean_df['Total_Bathrooms'] = (clean_df['FullBath'] + (0.5 * clean_df['HalfBath']) + clean_df['BsmtFullBath'] + (0.5 * clean_df['BsmtHalfBath']))
    clean_df["AllSF"] = clean_df["GrLivArea"] + clean_df["TotalBsmtSF"]
    clean_df["AvgSqFtPerRoom"] = clean_df["GrLivArea"] / (clean_df["TotRmsAbvGrd"] +
                                                       clean_df["FullBath"] +
                                                       clean_df["HalfBath"] +
                                                       clean_df["KitchenAbvGr"])

    clean_df["totalFlrSF"] = clean_df["1stFlrSF"] + clean_df["2ndFlrSF"]

    final_df = clean_df

    return final_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser("transform")
    parser.add_argument("--clean_data", type=str, help="Path to prepped data")
    parser.add_argument("--transformed_data", type=str, help="Path of output data")

    args = parser.parse_args()

    clean_data = args.clean_data
    transformed_data = args.transformed_data
    main(clean_data, transformed_data)
