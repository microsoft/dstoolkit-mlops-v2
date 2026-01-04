"""Configuration utils to load config from yaml/json."""
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import yaml


class DataAssetProvider:
    """
    Provides consistent data asset access with fallback to synthetic data generation.

    This class handles:
    - Loading registered data assets from Azure ML
    - Falling back to synthetic data if asset doesn't exist
    - Allowing models to work without pre-registered datasets
    """

    def __init__(self, ml_client, pipeline_config: Dict[str, Any]):
        """
        Initialize DataAssetProvider.

        Args:
            ml_client: Azure ML MLClient instance
            pipeline_config: Pipeline configuration dict from config.yaml
        """
        self.ml_client = ml_client
        self.pipeline_config = pipeline_config
        self.allow_synthetic_fallback = pipeline_config.get("allow_synthetic_fallback", False)
        self.synthetic_config = pipeline_config.get("synthetic_data_config", {})

    def get_data_asset(self, asset_name: str, asset_type: str = "uri_folder"):
        """
        Get data asset with fallback to synthetic data.

        Args:
            asset_name: Name of the registered data asset
            asset_type: Type of asset (uri_folder, uri_file, mltable)

        Returns:
            Data asset or synthetic data path

        Raises:
            ValueError: If asset not found and synthetic fallback not allowed
        """
        try:
            registered_asset = self.ml_client.data.get(name=asset_name, label="latest")
            return registered_asset
        except Exception as e:
            if self.allow_synthetic_fallback:
                return self._generate_synthetic_data()
            else:
                raise ValueError(
                    f"Data asset '{asset_name}' not found and synthetic fallback not enabled. "
                    f"Either register the data asset or set 'allow_synthetic_fallback: true' in config.yaml"
                ) from e

    def _generate_synthetic_data(self) -> str:
        """
        Generate synthetic data based on model type.

        Returns:
            Path to generated synthetic data directory
        """
        model_type = self.pipeline_config.get("model_type")

        if model_type == "sequence_model":
            from src.sequence_model.common.synthetic_data import save_synthetic_data

            num_sequences = self.synthetic_config.get("num_sequences", 100)
            sequence_length = self.synthetic_config.get("sequence_length", 20)

            # Create directory for synthetic data
            synthetic_dir = os.path.abspath(os.path.join(os.getcwd(), "outputs/synthetic_data"))
            os.makedirs(synthetic_dir, exist_ok=True)

            # Save pickle file inside the directory
            pickle_path = os.path.join(synthetic_dir, "train.pkl")
            save_synthetic_data(pickle_path, num_sequences=num_sequences, sequence_length=sequence_length)

            return synthetic_dir
        else:
            raise NotImplementedError(
                f"Synthetic data generation not implemented for model_type: {model_type}"
            )

    def get_asset_id_for_pipeline(self, asset_name: str) -> str:
        """
        Get asset ID suitable for use in AML pipeline Input.

        Args:
            asset_name: Name of the registered data asset

        Returns:
            Asset ID (registered) or local path (synthetic)
        """
        try:
            asset = self.get_data_asset(asset_name)
            # If it's a registered asset, use its ID
            return asset.id if hasattr(asset, 'id') else asset
        except ValueError:
            # If fallback is enabled, get synthetic path
            if self.allow_synthetic_fallback:
                return self._generate_synthetic_data()
            raise


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

        available = ', '.join(sorted(self.pipeline_configs.keys()))
        raise KeyError(
            f"Pipeline config '{pipelineconfig_name}' not found in {self.config_path}. "
            f"``pipeline_configs`` keys: {available}"
        )

    def get_deployment_config(self, deployment_name: str) -> Dict:
        """Get the pipeline configuration for given pipeline name and environment."""
        deploymentconfig_name = f"{deployment_name}_{self._environment}"
        if deploymentconfig_name in self.deployment_configs:
            return self.deployment_configs[deploymentconfig_name]

        available = ', '.join(sorted(self.deployment_configs.keys()))
        raise KeyError(
            f"Deployment config '{deploymentconfig_name}' not found in {self.config_path}. "
            f"``deployment_configs`` keys: {available}"
        )


if __name__ == "__main__":
    mlconfig = MLOpsConfig()
