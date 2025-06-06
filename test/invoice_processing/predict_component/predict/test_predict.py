import os
import unittest
from unittest.mock import ANY, patch, MagicMock
from src.invoice_processing.predict_component.predict.data_extraction.models.extraction_response import (
    ExtractionResponse,
    Invoice,
    LineItem,
    Provider,
    ServiceFor
)

from src.invoice_processing.predict_component.predict.predict import predict, main, process


class TestPredictFunctions(unittest.TestCase):
    @patch('src.invoice_processing.predict_component.predict.data_extraction.data_extractor_factory.DataExtractorFactory.create')
    @patch('os.makedirs')
    @patch('src.invoice_processing.predict_component.predict.predict.glob_by_extesion')
    @patch('src.invoice_processing.predict_component.predict.predict.MLFlowLogger')
    @patch('src.invoice_processing.predict_component.predict.predict.mlflow')
    @patch('src.invoice_processing.predict_component.predict.predict.process')
    @patch('pandas.DataFrame.to_csv')
    def test_predict(self, mock_to_csv, mock_process, mock_mlflow, mock_logger, mock_glob, mock_makedirs, mock_factory_create):
        mock_extractor = MagicMock()
        mock_factory_create.return_value = mock_extractor
        mock_process.return_value = ExtractionResponse(
            invoice=Invoice(
                totalClaimAmount=0.0,
                provider=Provider(
                    name=""
                ),
                serviceFor=ServiceFor(
                    name=""
                ),
                lineItems=[
                    LineItem(
                        amount=0.0,
                        text="",
                        transactionType="",
                        serviceStartDate="",
                        serviceEndDate=""
                    )
                ]
            )
        )
        mock_glob.return_value = ['file1.png', 'file2.jpg']
        azure_openai_endpoint = "https://example.com"
        azure_openai_api_key = "test_api_key"

        predict('gpt_only', 0, 'gpt-4o', azure_openai_endpoint, azure_openai_api_key,
                "{'prompt_name':'medical_claim_reimbursement','line_item_instructions':'complex'}",
                'test_data', 'prediction_path')

        mock_mlflow.log_params.assert_any_call({
            "gpt_deployment_name": "gpt-4o",
            "temperature": 0,
            "prompt_name": "medical_claim_reimbursement",
            "line_item_instructions": "complex"
        })

        mock_factory_create.assert_called_once_with('invoice', 'gpt_only', {
            "azure_openai_endpoint": azure_openai_endpoint,
            "azure_openai_api_key": azure_openai_api_key,
            "gpt_deployment_name": 'gpt-4o',
            "temperature": 0,
            "prompt_config": {'prompt_name': 'medical_claim_reimbursement', 'line_item_instructions': 'complex'}
        }, ANY)
        mock_makedirs.assert_called_once_with('prediction_path', exist_ok=True)
        self.assertEqual(mock_process.call_count, 2)

    @patch('src.invoice_processing.predict_component.predict.predict.convert_image_to_base64')
    @patch('src.invoice_processing.predict_component.predict.predict.save_output_as_json')
    @patch('src.invoice_processing.predict_component.predict.predict.Extractor')
    def test_process(self, mock_extractor, mock_save_output_as_json, mock_convert_image_to_base64):
        mock_convert_image_to_base64.return_value = "IMAGINE_I_AM_BASE64"
        mock_extractor.extract_data.return_value = ExtractionResponse(
            invoice=Invoice(
                provider=Provider(
                    name="Bob"
                ),
                serviceFor=ServiceFor(
                    name="Greg"
                ),
                lineItems=[],
                totalClaimAmount=0.99
            )
        )
        input_path = 'file1.png'
        output_path = 'output_path'
        process(mock_extractor, input_path, output_path)
        mock_extractor.extract_data.assert_called_once_with("IMAGINE_I_AM_BASE64")
        output_file_path = os.path.join(output_path, "file1_result.json")
        mock_save_output_as_json.assert_called_once_with(mock_extractor.extract_data.return_value.model_dump(), output_file_path)

    @patch('src.invoice_processing.predict_component.predict.predict.predict')
    def test_main(self, mock_predict):
        main('gpt_only',0 , 'gpt-4o', "https://example.com", "test_api_key",
             "{'prompt_name':'claim_reimbursement','line_item_instructions':'complex'}",
             'test_data', 'prediction_path')

        mock_predict.assert_called_once_with('gpt_only', 0,'gpt-4o', "https://example.com", "test_api_key",
                                             "{'prompt_name':'claim_reimbursement','line_item_instructions':'complex'}",
                                             'test_data', 'prediction_path')


if __name__ == '__main__':
    unittest.main()
