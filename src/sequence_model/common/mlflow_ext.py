"""Extension Module for MLFlow."""

# flake8: noqa

import logging
from argparse import Namespace

from mlflow import *

logger = logging.getLogger("mlflow_utils")


def init_run(
    command_line_args: Namespace = None,
    run_tags: dict = {},
    job_config: dict = {},
    mlflow_config: dict = {},
) -> tuple:
    """Initialize Job mlflow.

    Starts auto logger.
    Log command line arguments and job config as parameters.
    Set job tags.

    Args:
        command_line_args (Namespace): Parsed command line arguments.
        run_tags (dict): Job run tags.
        job_config (dict): Job configuration.
        mlflow_config (dict): Mlflow Configuration.

    Returns:
        tuple: (Current Id, Parent Id or None)
    """
    if mlflow_config:
        if mlflow_config.get("local_tracking", False) is True:
            set_tracking_uri("")

    autolog()

    params = vars(command_line_args) | job_config
    if params:
        log_params(params)

    if run_tags:
        set_tags(run_tags)

    return get_mlflow_run_ids()


def get_parent_run_id(current_run_id: str = None) -> str:
    """Get Parent run id.

    Returns:
        str: Parents run id.
    """
    current_run_id = current_run_id if current_run_id else active_run().info.run_id
    parent_run = get_parent_run(run_id=current_run_id)
    if parent_run:
        return parent_run.info.run_id
    else:
        return None


def get_mlflow_run_ids() -> tuple:
    """Get mlflow job run ids.

    Returns:
        tuple: (Current Id, Parent Id or None)
    """
    current_run_id: str = None
    parent_run_id: str = None

    current_run = active_run()

    if current_run is None:
        current_run = start_run()

    current_run_id = current_run.info.run_id

    logger.info(f"Current run_id {current_run_id}")

    parent_run_id = get_parent_run_id(current_run_id)

    logger.info(f"Parent run_id: {parent_run_id}")

    return (current_run_id, parent_run_id)


def set_propagated_tag(key: str, value: any):
    """Propagate Tags.

    Args:
        key (str): Name of tag.
        value (any): Value for tag.
    """
    if key and value:
        set_propagated_tags({key: value})


def set_propagated_tags(tags: dict):
    """Propagate Tags.

    Args:
        tags (dict): Dictionary of tags.
    """
    if tags:
        set_tags(tags)
        set_experiment_tags(tags)


def log_propagated_metric(name: str, value: float, parent_run_id: str = None):
    """Log metrics to Current and Parent job with MLflow.

    Args:
        name (str): Metrics name.
        value (float): Metrics value.
        parent_run_id (str): Parent Job Id. Defaults to None.
    """
    log_propagated_metrics(metrics={name: value}, parent_run_id=parent_run_id)


def log_propagated_metrics(metrics: dict, parent_run_id: str = None):
    """Log metrics to Current and Parent job with MLflow.

    Args:
        metrics (dict): Metrics to log.
        parent_run_id (str): Parent Job Id. Defaults to None.
    """
    logger.debug(f"Logging metrics: {metrics}")

    log_metrics(metrics=metrics)

    parent_run_id = get_parent_run_id() if parent_run_id is None else parent_run_id

    if parent_run_id:
        log_metrics(metrics=metrics, run_id=parent_run_id)


def get_metrics(run_id: str) -> dict:
    """Get Job Metrics.

    Args:
        run_id (str): Job metrics to retrieve

    Returns:
        dict: Job Metrics
    """
    metrics = None
    run = get_run(run_id=run_id)
    if run:
        metrics = run.data.metrics
    return metrics
