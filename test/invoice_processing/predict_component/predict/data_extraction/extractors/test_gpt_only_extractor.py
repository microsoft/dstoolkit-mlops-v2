import unittest
from unittest.mock import patch
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion, ParsedChoice, ParsedChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

from src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor import (
    GPTOnlyExtractor
)
from src.invoice_processing.predict_component.predict.data_extraction.models.extraction_response import (
    ExtractionResponse,
    Invoice,
    LineItem,
    Provider,
    ServiceFor
)


class TestGPTOnlyExtractor(unittest.TestCase):
    @patch('src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor.AzureOpenAI')
    @patch('src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor.LoggerProxy')
    @patch('src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor.GPTOnlyExtractor.create_prompt')
    def test_extract_data(self, mock_create_prompt, mock_logger_proxy, mock_azure_open_ai):
        mock_create_prompt.return_value = [
            {
                "role": "system",
                "content": "You are an AI assistant"
            },
            {"role": "user", "content": "Hi."}
        ]

        extraction_response = ExtractionResponse(
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
        mock_completion = ParsedChatCompletion(
            id="id",
            created=0,
            model="model",
            object="chat.completion",
            choices=[
                ParsedChoice(
                    message=ParsedChatCompletionMessage(
                        parsed=extraction_response,
                        role="assistant"
                    ),
                    index=0,
                    finish_reason="stop"
                )
            ],
            usage=CompletionUsage(
                completion_tokens=100,
                prompt_tokens=101,
                total_tokens=201
            )
        )
        mock_azure_open_ai_instance = mock_azure_open_ai.return_value
        mock_azure_open_ai_instance.beta.chat.completions.parse.return_value = mock_completion

        gpt_only_extractor = GPTOnlyExtractor({
            "azure_openai_endpoint": "https://example.com",
            "azure_openai_api_key": "SSSHHH",
            "gpt_deployment_name": 'gpt-4o',
            "temperature": 0,
            "prompt_config": {'prompt_name': 'medical_claim_reimbursement', 'line_item_instructions': 'complex'}
        }, mock_logger_proxy)
        result = gpt_only_extractor.extract_data("BASE64_STRING")

        self.assertEqual(result, extraction_response)
        mock_azure_open_ai_instance.beta.chat.completions.parse.assert_called_with(
            model='gpt-4o',
            temperature=0,
            messages=mock_create_prompt.return_value,
            response_format=ExtractionResponse
        )
        mock_logger_proxy.log_metric.assert_any_call("completion_tokens", 100)
        mock_logger_proxy.log_metric.assert_any_call("prompt_tokens", 101)

    @patch('src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor.PromptManager.get_prompt')
    @patch('src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor.AzureOpenAI')
    @patch('src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor.LoggerProxy')
    def test_create_prompt(self, mock_logger_proxy, mock_azure_open_ai, mock_get_prompt):
        mock_get_prompt.return_value = "Extract data from this invoice"

        gpt_only_extractor = GPTOnlyExtractor({
            "azure_openai_endpoint": "https://example.com",
            "azure_openai_api_key": "SSSHHH",
            "gpt_deployment_name": 'gpt-4o',
            "prompt_config": {'prompt_name': 'medical_claim_reimbursement', 'line_item_instructions': 'complex'}
        }, mock_logger_proxy)

        base64_image = "base64_image_string"
        messages = gpt_only_extractor.create_prompt(base64_image)

        self.assertEqual(messages, [
            {
                "role": "system",
                "content":
                    "You are an AI assistant that analyzes the text provided "
                    "and supplemented images and returns them as structured JSON objects. "
                    "Do not return as a code block."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": mock_get_prompt.return_value
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ]
            }
        ])

    @patch('src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor.AzureOpenAI')
    @patch('src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor.LoggerProxy')
    @patch('src.invoice_processing.predict_component.predict.data_extraction.extractors.gpt_only_extractor.GPTOnlyExtractor.create_prompt')
    def test_extract_data_with_retry(self, mock_create_prompt, mock_logger_proxy, mock_azure_open_ai):
        mock_create_prompt.return_value = [
            {
                "role": "system",
                "content": "You are an AI assistant"
            },
            {"role": "user", "content": "Hi."}
        ]

        mock_azure_open_ai_instance = mock_azure_open_ai.return_value
        mock_azure_open_ai_instance.beta.chat.completions.parse.side_effect = [Exception("Error"), Exception("Error"), ParsedChatCompletion(
            id="id",
            created=0,
            model="model",
            object="chat.completion",
            choices=[
                ParsedChoice(
                    message=ParsedChatCompletionMessage(
                        parsed=ExtractionResponse(
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
                        ),
                        role="assistant"
                    ),
                    index=0,
                    finish_reason="stop"
                )
            ],
            usage=CompletionUsage(
                completion_tokens=100,
                prompt_tokens=101,
                total_tokens=201
            )
        )]

        gpt_only_extractor = GPTOnlyExtractor({
            "azure_openai_endpoint": "https://example.com",
            "azure_openai_api_key": "SSSHHH",
            "gpt_deployment_name": 'gpt-4o',
            "prompt_config": {'prompt_name': 'medical_claim_reimbursement', 'line_item_instructions': 'complex'}
        }, mock_logger_proxy)
        result = gpt_only_extractor.extract_data("BASE64_STRING")

        self.assertIsNotNone(result)
        self.assertIsInstance(result, ExtractionResponse)
        self.assertEqual(mock_azure_open_ai_instance.beta.chat.completions.parse.call_count, 3)
        mock_logger_proxy.log_metric.assert_any_call("completion_tokens", 100)
        mock_logger_proxy.log_metric.assert_any_call("prompt_tokens", 101)

if __name__ == '__main__':
    unittest.main()
