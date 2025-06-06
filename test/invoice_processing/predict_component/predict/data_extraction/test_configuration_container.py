import unittest
from unittest.mock import patch, mock_open

from src.invoice_processing.predict_component.predict.data_extraction.config.configuration_container import (
    ConfigurationContainer
)


class TestConfigurationContainer(unittest.TestCase):

    def setUp(self):
        # Clear the config registry before each test
        ConfigurationContainer._config_registry = {}

    def test_register_and_get_config(self):
        config = {"key": "value"}
        ConfigurationContainer.register_config("extractor1", config)
        retrieved_config = ConfigurationContainer.get_config("extractor1")
        self.assertEqual(retrieved_config, config)

    def test_get_config_not_registered(self):
        retrieved_config = ConfigurationContainer.get_config("non_existent_extractor")
        self.assertEqual(retrieved_config, {})

    @patch("builtins.open", new_callable=mock_open, read_data='{"extractor2": {"key": "value"}}')
    @patch("json.load", return_value={"extractor2": {"key": "value"}})
    def test_load_configs_from_file(self, mock_json_load, mock_open):
        ConfigurationContainer.load_configs_from_file("dummy_path")
        self.assertEqual(ConfigurationContainer._config_registry["extractor2"], {"key": "value"})
