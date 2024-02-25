"""Configuration utils to load config from yaml/json."""
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import yaml


class MLOpsConfig:
    """MLopsConfig Class."""

    _raw_config: Any

    def __init__(
        self, environment: str = "pr", config_path: Path = "config/config.yaml"
    ):
        """Intialize MLConfig with yaml config data."""
        self.config_path = config_path
        self._environment = environment
        load_dotenv()
        with open(config_path, "r", encoding="utf-8") as stream:
            self._raw_config = yaml.safe_load(os.path.expandvars(stream.read()))

    def __getattr__(self, __name: str) -> Any:
        """Get values for top level keys in configuration."""
        return self._raw_config[__name]

    def get_pipeline_config(self, pipeline_name: str) -> Dict:
        """Get the pipeline configuration for given pipeline name and environment."""
        pipelineconfig_name = f"{pipeline_name}_{self._environment}"
        if pipelineconfig_name in self.pipeline_configs:
            return self.pipeline_configs[pipelineconfig_name]

    def get_deployment_config(self, deployment_name: str) -> Dict:
        """Get the pipeline configuration for given pipeline name and environment."""
        deploymentconfig_name = f"{deployment_name}_{self._environment}"
        if deploymentconfig_name in self.deployment_configs:
            return self.deployment_configs[deploymentconfig_name]


if __name__ == "__main__":
    mlconfig = MLOpsConfig()
