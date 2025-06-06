import os
import unittest
from unittest.mock import MagicMock

from src.invoice_processing.predict_component.predict.data_extraction.config.configuration_container import (
    ConfigurationContainer
)
from src.invoice_processing.predict_component.predict.data_extraction.data_extractor_factory import (
    DataExtractorFactory
)
from src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor import (
    GPTOnlyExtractor
)
from test.invoice_processing.predict_component.predict.data_extraction.assets.mock_extractor import MockExtractor


class TestDataExtractorFactory(unittest.TestCase):
    def setUp(self):
        self.assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        config_path = os.path.join(self.assets_path, "config.json")
        ConfigurationContainer.load_configs_from_file(config_path)
        self.additional_config = {
            "prompt_config": {
                "prompt_name": "medical_claim_reimbursement",
                "line_item_instructions": "complex"
            }
        }
        self.logger = MagicMock()
        DataExtractorFactory.register("mockextractor", "mock", MockExtractor)

    def test_load_default_extractors(self):
        DataExtractorFactory.load_default_extractors()
        extractor = DataExtractorFactory.create("invoice",
                                                "gpt_only",
                                                self.additional_config,
                                                self.logger)

        self.assertIsInstance(extractor, GPTOnlyExtractor)

    def test_create_extractor(self):
        extractor = DataExtractorFactory.create("mock",
                                                "mockextractor",
                                                self.additional_config,
                                                self.logger)

        self.assertIsInstance(extractor, MockExtractor)

        resp = extractor.extract_data("")
        self.assertEqual(resp.invoice.provider.name, "Mock Provider")
        self.assertEqual(resp.invoice.serviceFor.name, "Mock Patient")

    def test_create_extractor_invalid_category(self):
        with self.assertRaises(ValueError):
            DataExtractorFactory.create("invalid", "mock_ocr_extractor",
                                        self.additional_config,
                                        self.logger)

    def test_create_extractor_invalid_name(self):
        with self.assertRaises(ValueError):
            DataExtractorFactory.create("mock", "invalid_extractor",
                                        self.additional_config,
                                        self.logger)

    def test_list_categories(self):
        categories = DataExtractorFactory.list_categories()
        self.assertIn("mock", categories)

    def test_list_extractors(self):
        extractors = DataExtractorFactory.list_extractors("mock")
        self.assertIn("mockextractor", extractors)

    def test_register_invalid_extractor(self):
        with self.assertRaises(ValueError):
            DataExtractorFactory.register("invalid_extractor", "mock", object)

if __name__ == '__main__':
    unittest.main()
