import base64
import json
import logging

log = logging.getLogger(__name__)


def save_output_as_json(output, output_file_path):
    """
    Save response output as a JSON file.

    Args:
        output (dict): Output data to save.
        output_file_path (str): Path to the output file.
    """
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)
    log.info(f"Saved output to {output_file_path}")


def convert_image_to_base64(image_path: str) -> str:
    """
    Convert an image path to a base64 encoded string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded image string.
    """
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_image
