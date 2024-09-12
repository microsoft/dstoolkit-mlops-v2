"""

This module provides functionality for managing Azure Machine Learning model artifacts resources.
It includes functions to delete the Model Artifacts from Azure Machine Learning workspace based
on the user specified date.
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
    parser = argparse.ArgumentParser(description="Clean up Registered Model Artifacts")

    parser.add_argument(
        "--clean_up_date",
        type=str,
        required=True,
        help="Date before which all the models needs to be deleted",
    )

    return parser.parse_args()


def cleanup_models(models, clean_up_date):
    """Delete Registered models."""
    for model in models:
        if (model.created_time.date() < clean_up_date):
            print(f"Deleting Models {model.version} of model {model.name}")
            model.delete()
    print("Sucessfully Deleted Models")


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    print("DATE:", args.clean_up_date)

    """Register all datasets from the config file."""
    config = MLOpsConfig()

    ws = Workspace.get(
        name=config.aml_config["workspace_name"],
        subscription_id=config.aml_config["subscription_id"],
        resource_group=config.aml_config["resource_group_name"])

    models = Model.list(ws)
    clean_up_date = datetime.strptime(args.clean_up_date, '%Y-%m-%d').date()

    cleanup_models(models, clean_up_date)
