from .config.configuration_container import ConfigurationContainer
from .extractors.base_extractor import Extractor, LoggerProxy


class DataExtractorFactory:
    """Factory to dynamically load and manage data extractors by category."""

    _registry = {}

    @classmethod
    def load_default_extractors(cls) -> None:
        """Load default extractors into the factory registry."""
        from .extractors.gpt_only_extractor import GPTOnlyExtractor
        cls.register("gpt_only", "invoice", GPTOnlyExtractor)

    @classmethod
    def register(cls, name: str, category: str, extractor_cls: type) -> None:
        """Register a data extractor class under a category."""
        if not issubclass(extractor_cls, Extractor):
            raise ValueError(
                f"{extractor_cls} is not a subclass of Extractor"
            )
        if category not in cls._registry:
            cls._registry[category] = {}
        cls._registry[category][name] = extractor_cls

    @classmethod
    def list_categories(cls) -> list[str]:
        """List all available categories."""
        return list(cls._registry.keys())

    @classmethod
    def list_extractors(cls, category: str) -> list[str]:
        """List all extractors in a specific category."""
        if category not in cls._registry:
            raise ValueError(f"Category {category} is not registered")
        return list(cls._registry[category].keys())

    @classmethod
    def create(cls, category: str, name: str, additional_config: dict,
               logger_proxy: LoggerProxy) -> Extractor:
        """Create an instance of extractor by category and name."""
        if (category not in cls._registry or name not in cls._registry[category]):
            raise ValueError(
                f"Extractor {name} in category {category} is not registered"
            )
        # Get extractor class
        extractor_cls = cls._registry[category][name]

        # Get configuration from the ServiceContainer
        config = ConfigurationContainer.get_config(name)
        config.update(additional_config)

        # Instantiate the extractor with the configuration
        return extractor_cls(config, logger_proxy)
