import json
import logging
from python_retry import retry

from openai import AzureOpenAI
from .base_extractor import (
    Extractor,
    LoggerProxy
)
from ..models.extraction_response import (
    ExtractionResponse,
    Invoice,
    LineItem,
    Provider,
    ServiceFor
)
from ..prompts.prompt_manager import PromptManager

log = logging.getLogger(__name__)


class GPTOnlyExtractor(Extractor):
    """
    Extraction implementation use Azure OpenAI Model
    Args:
            config (dict): The configuration dictionary. the following values are expected:
                - azure_openai_endpoint (str): Azure OpenAI endpoint.
                - azure_openai_api_key (str): Azure OpenAI API key.
                    (optional, either provide azure_openai_api_key, or a token_provider).
                - api_version (str): Azure OpenAI API version.
                - token_provider (lambda: str): OAuth JWT token provider method.
                    (optional, either provide azure_openai_api_key, or a token_provider).
                - custom_hdeaders (str): Custom headers to add to the request to OpenAI.
                - gpt_deployment_name (str): Azure OpenAI API deployment name.
                - prompt_config (dict): Prompt configuration.
            logger_proxy (LoggerProxy): Metrics logger.
    """

    def __init__(self, config: dict, logger_proxy: LoggerProxy):
        self.client = AzureOpenAI(
            azure_endpoint=config.get("azure_openai_endpoint"),
            api_key=config.get("azure_openai_api_key"),
            api_version=config.get("api_version", "2024-08-01-preview"),
            azure_ad_token_provider=config.get("token_provider"),
            default_headers=config.get("custom_headers")
        )
        self.gpt_deployment_name = config.get("gpt_deployment_name")
        self.prompt_config = config.get('prompt_config', {})
        self.temperature = config.get('temperature', 0.0)
        super().__init__(config, logger_proxy)

    @retry(
        retry_on=(Exception,),
        max_retries=5,
        backoff_factor=2,
        retry_logger=log
    )
    def extract_data(self, file) -> ExtractionResponse:
        """
        Process an input file using the Azure OpenAI model and save the output.

        Args:
            input_path (str): Path to an input image file.
            output_folder (str): Path to the output folder.

        Returns:
            Optional[InvoiceData]: Parsed response from the model.
        """
        messages = self.create_prompt(file)

        completion = self.client.beta.chat.completions.parse(
            model=self.gpt_deployment_name,
            messages=messages,
            response_format=ExtractionResponse,
            temperature=self.temperature
        )

        if completion and completion.choices and completion.choices[0].message.parsed:
            event = completion.choices[0].message.parsed
            log.debug(completion.model_dump_json(indent=2))
            self.logger_proxy.log_metric("completion_tokens", completion.usage.completion_tokens)
            self.logger_proxy.log_metric("prompt_tokens", completion.usage.prompt_tokens)

            event.metadata = {
                "completion_tokens": completion.usage.completion_tokens,
                "prompt_tokens": completion.usage.prompt_tokens
            }
            return event
        else:
            log.error("No completion returned or no choices in completion.")
            return None

    def create_prompt(self, base64_image):
        """
        Create a prompt for the Azure OpenAI model.

        Args:
            base64_image (str): Base64 encoded image string.

        Returns:
            List[dict]: List of messages for the prompt.
        """
        structure = ExtractionResponse(
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
        ).model_dump()

        user_prompt = PromptManager.get_prompt(
            self.prompt_config["prompt_name"],
            line_item_instructions=self.prompt_config["line_item_instructions"],
            structure={json.dumps(structure)}
        )

        user_prompt_formatted_with_image = [
            {
                "type": "text",
                "text": (
                    user_prompt
                )
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            }
        ]

        messages = [
            {
                "role": "system",
                "content":
                    "You are an AI assistant that analyzes the text provided "
                    "and supplemented images and returns them as structured JSON objects. "
                    "Do not return as a code block."
            },
            {"role": "user", "content": user_prompt_formatted_with_image}
        ]

        return messages
