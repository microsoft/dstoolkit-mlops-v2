import mlflow
from .data_extraction.extractors.base_extractor import (
    LoggerProxy
)


class MLFlowLogger(LoggerProxy):
    def log_metric(self, key: str, value: float) -> None:
        mlflow.log_metric(key, value)
