"""
utils.py

This module contains various utility functions that can be used across
different parts of the project.

Functions:
    read_json_file(file_path):
        Reads a JSON file and returns the parsed data.
    normalize_string(value):
        Normalize string by stripping extra whitespace and converting to lowercase.
    load_csv_file(file_path):
        Reads a CSV file and returns the parsed data.
"""

import json
from pathlib import Path
from typing import Union, List
import re
import logging
from dateutil.parser import parse

log = logging.getLogger(__name__)


def load_json_file(path: Union[str, Path]):
    """
    Reads a JSON file and returns the parsed data.
    Args:
        file_path (str): The path to the JSON file to be read.
    Returns:
        dict: The parsed JSON data as a dictionary.
    Raises:
        FileNotFoundError
    """
    # Load ground truth data
    all_data = []
    all_data_dict = {}
    data_path = Path(path)
    if data_path.is_dir():
        # Multiple files in a directory
        for file_path in data_path.glob("*.json"):
            log.debug(f"file_path: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    curr_data = json.load(f)
                    # For ground truth format
                    if isinstance(curr_data, List):
                        all_data = all_data + curr_data
                    # For predictions data format
                    else:
                        all_data_dict[str(file_path)] = curr_data
            except FileNotFoundError:
                log.error(f"Error: The file at {file_path} was not found")
            except json.JSONDecodeError:
                log.error(f"Error: The file at {file_path} is not a valid JSON")
    else:
        # Single file
        try:
            with open(path, "r", encoding="utf-8") as f:
                curr_data = json.load(f)
                # For ground truth format
                if isinstance(curr_data, List):
                    all_data = all_data + curr_data
                # For predictions data format
                else:
                    all_data_dict[str(file_path)] = curr_data
        except FileNotFoundError:
            log.error(f"Error: The file at {file_path} was not found")
        except json.JSONDecodeError:
            log.error(f"Error: The file at {file_path} is not a valid JSON")
    if len(all_data) > 1:
        return all_data
    else:
        return all_data_dict


def normalize_string(value: str) -> str:
    """
    Normalize string by stripping extra whitespace and converting to lowercase.
    """
    if not isinstance(value, str):
        return str(value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    value = re.sub(r"\(\s*", "(", value)
    value = re.sub(r"\s*\)", ")", value)
    value = re.sub(r"day\s*\(s\)", "days", value)
    return value


def preprocess_amount(amount):
    """
    Amount pre-processing - remove parentheses and
    white spaces from amount string
    """
    parsed_amount = ""
    if isinstance(amount, str):
        parsed_amount = amount.strip()
        parsed_amount = parsed_amount.replace("(", "").replace(")", "")
        if len(parsed_amount) == 0:
            parsed_amount = "0"
    else:
        parsed_amount = amount
    return parsed_amount


def preprocess_date(date_str):
    """
    Date preprocessing - remove whitespaces and parse
    date string into date object
    """
    date_str = date_str.strip()
    date = parse(date_str)
    return date
