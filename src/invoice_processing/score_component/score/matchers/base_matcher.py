"""This class is an interface."""
from abc import ABC, abstractmethod


class BaseMatcher(ABC):
    """Abstract class to define matcher base functions."""

    @abstractmethod
    def get_match(self):
        """Get match result per line item."""
        pass

    @abstractmethod
    def get_matcher_name(self):
        """Return matcher name."""
        pass
