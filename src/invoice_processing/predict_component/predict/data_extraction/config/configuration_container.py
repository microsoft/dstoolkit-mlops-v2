"""Container for storing configurations of extractors."""
class ConfigurationContainer:
    """A simple service container to store configurations for extractors."""

    _config_registry = {}

    @classmethod
    def register_config(cls, extractor_name: str, config: dict):
        """Register configuration for a specific extractor."""
        cls._config_registry[extractor_name] = config

    @classmethod
    def get_config(cls, extractor_name: str) -> dict:
        """Retrieve the configuration for a specific extractor."""
        if extractor_name not in cls._config_registry:
            return {}
        return cls._config_registry[extractor_name]

    @classmethod
    def load_configs_from_file(cls, filepath: str):
        """Load configurations from a JSON file."""
        import json
        with open(filepath, 'r') as f:
            configs = json.load(f)
        for extractor_name, config in configs.items():
            cls.register_config(extractor_name, config)
