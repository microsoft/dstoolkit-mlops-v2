"""This module provides a logger that integrates with MLflow for logging metrics."""
import mlflow
from .data_extraction.extractors.base_extractor import (
    LoggerProxy
)


class MLFlowLogger(LoggerProxy):
    """Logger that integrates with MLflow for logging metrics."""

    def log_metric(self, key: str, value: float) -> None:
        """Log a metric with a key and value using MLflow."""
        mlflow.log_metric(key, value)
