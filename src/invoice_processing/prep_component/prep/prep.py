"""This module contains the preprocessing step for invoice processing."""
import argparse
import os
import random
import shutil
import logging
import mlflow

log = logging.getLogger(__name__)


def sample_data(data_paths, samples_amount, sampling_seed):
    """
    Take a sample of data paths based on the specified amount and seed.

    Parameters:
      data_paths (str): paths to files
      samples_amount (int): amount of samples to randomly use from the data set, 0 means all
      sampling_seed (int): seed for random sampling of dataset, -1 means no seed
    """
    sampled_data_paths = data_paths
    if samples_amount > 0:
        data_paths_len = len(data_paths)

        if sampling_seed != -1:
            random.seed(sampling_seed)

        sampled_data_paths = random.sample(data_paths, samples_amount)
        print(f"filtered samples array from {data_paths_len} to {len(data_paths)}")
        print(sampled_data_paths)

    return sampled_data_paths


def main(raw_data, prep_data, samples_amount, sampling_seed):
    """
    Read existing jpg and png files and invoke preprocessing step.

    Parameters:
      raw_data (str): a folder to read csv files
      prep_data (str): a folder for preprocessed data
      samples_amount (int): amount of samples to randomly use from the data set, 0 means all
      sampling_seed (int): seed for random sampling of dataset, -1 means no seed
    """
    mlflow.log_param('number_of_samples', samples_amount)

    lines = [
        f"Raw data path: {raw_data}",
        f"Data output path: {prep_data}",
    ]

    for line in lines:
        log.info(line)

    data_paths = os.listdir(raw_data)
    log.debug(f"mounted_path files: {data_paths}")

    data_paths = sample_data(data_paths, samples_amount, sampling_seed)

    os.makedirs(prep_data, exist_ok=True)
    for filename in data_paths:
        log.info("reading file: %s ..." % filename)
        destination = os.path.join(prep_data, filename)
        source = os.path.join(raw_data, filename)
        shutil.copy(source, destination)
        log.info("saving file: %s ..." % destination)


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
    parser.add_argument(
        "--samples_amount", required=False, type=int, default=0,
        help="Amount of samples to randomly use from the data set, 0 means all,"
    )
    parser.add_argument(
        "--sampling_seed", required=False, type=int, default=-1,
        help="Seed for random sampling of dataset, -1 means no seed,"
    )

    args = parser.parse_args()

    log.debug("Prep started... arguments parsed successfully.")

    main(args.raw_data, args.prep_data, args.samples_amount, args.sampling_seed)
