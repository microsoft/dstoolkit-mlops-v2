"""This class is an interface."""
from abc import ABC, abstractmethod

from ..models.extraction_response import (
    ExtractionResponse
)


class LoggerProxy(ABC):
    """Abstract class to define logging functionalities."""

    @abstractmethod
    def log_metric(self, key: str, value: float) -> None:
        """Log a metric with a key and value."""
        pass


class Extractor(ABC):
    """Abstract class to define extractor functionalities and data."""

    def __init__(self, config: dict, logger_proxy: LoggerProxy):
        """Initialize the Extractor with the provided configuration and logger."""
        self.config = config
        self.logger_proxy = logger_proxy

    @abstractmethod
    def extract_data(self, file) -> ExtractionResponse:
        """Extract structured data from the given the input."""
        pass
