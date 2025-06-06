"""
Utility functions for invoice processing scoring component.

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
from typing import Union
import re
import logging
from dateutil.parser import parse

log = logging.getLogger(__name__)


def _load_json_from_file(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            curr_data = json.load(f)
            return curr_data
    except FileNotFoundError:
        log.error(f"Error: The file at {file_path} was not found")
    except json.JSONDecodeError:
        log.error(f"Error: The file at {file_path} is not a valid JSON")
    return None


def _load_json_from_directory(directory_path):
    """Load JSON data from all files in a directory."""
    all_data = []
    all_data_dict = {}
    for file_path in Path(directory_path).glob("*.json"):
        log.debug(f"file_path: {file_path}")
        curr_data = _load_json_from_file(file_path)
        if curr_data is not None:
            if isinstance(curr_data, list):
                all_data += curr_data
            else:
                all_data_dict[str(file_path)] = curr_data
    return all_data, all_data_dict


def load_json_file(path: Union[str, Path]):
    """
    Read a JSON file and returns the parsed data.

    Args:
        file_path (str): The path to the JSON file to be read.
    Returns:
        dict: The parsed JSON data as a dictionary.
    Raises:
        FileNotFoundError
    """
    data_path = Path(path)
    if data_path.is_dir():
        all_data, all_data_dict = _load_json_from_directory(data_path)
    else:
        all_data = []
        all_data_dict = {}
        curr_data = _load_json_from_file(data_path)
        if curr_data is not None:
            if isinstance(curr_data, list):
                all_data += curr_data
            else:
                all_data_dict[str(data_path)] = curr_data
    if len(all_data) > 1:
        return all_data
    else:
        return all_data_dict


def normalize_string(value: str) -> str:
    """Normalize string by stripping extra whitespace and converting to lowercase."""
    if not isinstance(value, str):
        return str(value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    value = re.sub(r"\(\s*", "(", value)
    value = re.sub(r"\s*\)", ")", value)
    value = re.sub(r"day\s*\(s\)", "days", value)
    return value


def preprocess_amount(amount):
    """Remove parentheses and white spaces from amount string."""
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
    """Remove whitespaces and parse date string into date object."""
    date_str = date_str.strip()
    date = parse(date_str)
    return date
