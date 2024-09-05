"""
This module provides functionality for managing Azure Machine Learning model artifacts resources.

It includes functions to get the Model Artifacts from Azure Machine Learning workspace based on the user specified date.
The module uses the Azure Machine Learning SDK for Python to interact with Azure resources.
"""

import argparse
from mlops.common.config_utils import MLOpsConfig
from datetime import datetime

from azureml.core import Workspace
from azureml.core.model import Model
import logging

logger = logging.getLogger(__name__)


def parse_args():
    """Parse arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Get the Registered Model Artifacts ready for clean up")

    parser.add_argument(
        "--clean_up_date",
        type=str,
        required=True,
        help="Date before which all the models needs to be deleted",
    )

    return parser.parse_args()


def get_models(models, clean_up_date):
    """Get Registered models Artifacts."""
    for model in models:
        if (model.created_time.date() < clean_up_date):
            print(f"Models ready to be Deleted: Model version {model.version} of model {model.name}")


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    print("DATE:", args.clean_up_date)

    """Get information from the config file."""
    config = MLOpsConfig()

    ws = Workspace.get(
        name=config.aml_config["workspace_name"],
        subscription_id=config.aml_config["subscription_id"],
        resource_group=config.aml_config["resource_group_name"])

    print("ws:", ws)
    print("name:", config.aml_config["workspace_name"])
    print("subscription_id:", config.aml_config["subscription_id"])
    print("resource_group:", config.aml_config["resource_group_name"])

    models = Model.list(ws)
    clean_up_date = datetime.strptime(args.clean_up_date, '%Y-%m-%d').date()

    get_models(models, clean_up_date)
