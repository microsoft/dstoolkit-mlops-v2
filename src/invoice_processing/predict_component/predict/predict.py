"""This module contains the predict function for the invoice processing component."""
import ast
import os
import argparse
import time
from glob import glob
import logging
import mlflow
import pandas as pd


from .data_extraction.data_extractor_factory import (
    DataExtractorFactory
)
from .data_extraction.extractors.base_extractor import (
    Extractor
)
from .data_extraction.models.extraction_response import (
    ExtractionResponse
)
from .mlflow_logger import MLFlowLogger
from .helpers import convert_image_to_base64, save_output_as_json

log = logging.getLogger(__name__)


def predict(
    strategy,
    temperature,
    gpt_deployment_name,
    azure_openai_endpoint,
    azure_openai_api_key,
    prompt_config,
    test_data,
    prediction_path,
) -> None:
    """
    Perform data extraction using the specified orchestration strategy and Azure OpenAI model.

    This includes:
        - Initializing the Azure OpenAI client.
        - Creating prompt messages for the model.
        - Processing each file in the input folder.
        - Saving the output as a JSON file in the output folder.

    Args:
        strategy (string): orchestration strategy name
        temperature (float): LLM temperature
        gpt_deployment_name (string): name of the GPT deployment name to use
        prompt_config (string): dictionary loaded as string with prompt configuration
        test_data (str): a folder with input data
        prediction_path (str): a folder for storing predictions
    """
    config_dict = ast.literal_eval(prompt_config)
    params = {
        "gpt_deployment_name": gpt_deployment_name,
        "temperature": temperature,
        "prompt_name": config_dict["prompt_name"],
        "line_item_instructions": config_dict["line_item_instructions"]
    }
    mlflow.log_params(params)

    DataExtractorFactory.load_default_extractors()
    extractor = DataExtractorFactory.create("invoice", strategy, {
        "azure_openai_endpoint": azure_openai_endpoint,
        "azure_openai_api_key": azure_openai_api_key,
        "gpt_deployment_name": gpt_deployment_name,
        "temperature": temperature,
        "prompt_config": config_dict
    }, MLFlowLogger())

    mlflow.log_param("strategy", strategy)

    os.makedirs(prediction_path, exist_ok=True)

    test_data_paths = glob_by_extesion(test_data, ['.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG'])

    log.info(f"Processing files in {test_data} using model/strategy {strategy}, len_imgs:  {len(test_data_paths)}")
    mlflow.log_metric('images_identified',
                      len(test_data_paths))

    performance_df = pd.DataFrame(columns=[
        'file_path',
        'completion_tokens',
        'prompt_tokens',
        'execution_time'
    ])
    for file in test_data_paths:
        file_path = os.path.join(test_data, file)
        try:
            extraction_response, execution_time = process(extractor, file_path, prediction_path)
            mlflow.log_metric("execution_time", execution_time)
            log.info(f"Execution time for {gpt_deployment_name}: {execution_time} seconds")

            performance_df = pd.concat([pd.DataFrame([[
                file_path,
                extraction_response.metadata.get("completion_tokens"),
                extraction_response.metadata.get("prompt_tokens"),
                execution_time
            ]], columns=performance_df.columns), performance_df], ignore_index=True)
        except Exception as e:
            log.error(f"Error processing file {file}: {e}")

    performance_df_path = "performance_results.csv"
    performance_df.to_csv(f"{performance_df_path}", index=False)
    mlflow.log_artifact(f"{performance_df_path}")

    mlflow.log_metric('successfully_processed_images', len(performance_df.index))

    for column in ['completion_tokens', 'prompt_tokens', 'execution_time']:
        mean = performance_df.loc[:, column].mean()
        median = performance_df.loc[:, column].median()
        total = performance_df.loc[:, column].sum()
        mlflow.log_metric(f"mean_{column}", mean)
        mlflow.log_metric(f"median_{column}", median)
        mlflow.log_metric(f"total_{column}", total)

    total_input_price, total_output_price = estimate_cost(gpt_deployment_name, performance_df)
    mlflow.log_metric("estimated_input_price", total_input_price)
    mlflow.log_metric("estimated_output_price", total_output_price)


def estimate_cost(gpt_deployment_name, performance_df):
    """Estimate the cost of processing based on the number of tokens used."""
    total_input_tokens = performance_df.loc[:, 'prompt_tokens'].sum()
    total_output_tokens = performance_df.loc[:, 'completion_tokens'].sum()
    if gpt_deployment_name == 'gpt-4o':
        input_price_in_usd = 2.5
        output_price_in_usd = 10
    elif gpt_deployment_name == 'gpt-4o-mini':
        input_price_in_usd = 0.15
        output_price_in_usd = 0.6
    else:
        input_price_in_usd = 0
        output_price_in_usd = 0
        log.error(f"{gpt_deployment_name} not included in estimate_cost function, "
                  + "please add price logic to estimate cost")
    per_one_mln_tokens = 1000000
    total_input_price = total_input_tokens * (input_price_in_usd / per_one_mln_tokens)
    total_output_price = total_output_tokens * (output_price_in_usd / per_one_mln_tokens)
    return total_input_price, total_output_price


def glob_by_extesion(test_data, types):
    """Glob files by extension in the specified test data directory."""
    all_images = []
    for type in types:
        arr = glob(f'{test_data}/*{type}')
        all_images += arr
    return all_images


def process(extractor: Extractor, input_path, output_folder) -> tuple[ExtractionResponse, float]:
    """Process a single input file and return the extraction response and execution time."""
    base64_image = convert_image_to_base64(input_path)

    start_time = time.time()
    extraction_response = extractor.extract_data(base64_image)
    end_time = time.time()
    execution_time = end_time - start_time

    json_base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_file_path = os.path.join(output_folder, f"{json_base_name}_result.json")
    save_output_as_json(extraction_response.model_dump(), output_file_path)
    return extraction_response, execution_time


def main(
    strategy,
    temperature,
    gpt_deployment_name,
    azure_openai_endpoint,
    azure_openai_api_key,
    prompt_config,
    test_data,
    prediction_path,
):
    """Load test data, call predict function.

    Args:
        strategy (string): orchestration strategy name
        temperature (float): LLM temperature
        gpt_deployment_name (string): name of the GPT deployment name to use
        prompt_config (string): dictionary with prompt configuration
        test_data (string): path to test data
        prediction_path (string): path to which to write predictions
    """
    lines = [
        f"Orchestration strategy: {strategy}",
        f"Temperature: {temperature}",
        f"GPT deployment name: {gpt_deployment_name}",
        f"Predict configuration: {prompt_config}",
        f"Test data path: {test_data}",
        f"Predictions path: {prediction_path}",
    ]

    for line in lines:
        log.info(line)

    predict(
        strategy,
        temperature,
        gpt_deployment_name,
        azure_openai_endpoint,
        azure_openai_api_key,
        prompt_config,
        test_data,
        prediction_path,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("predict")
    parser.add_argument("--strategy", type=str, help="Orchestration strategy")
    parser.add_argument("--temperature", type=float, help="LLM temperature")

    parser.add_argument("--gpt_deployment_name", type=str, help="GPT deployment name")
    parser.add_argument(
        "--azure_openai_endpoint", type=str, help="Azure OpenaAI endpoint"
    )
    parser.add_argument(
        "--azure_openai_api_key", type=str, help="Azure OpenaAI API key"
    )
    parser.add_argument("--prompt_config", type=str, help="Config dictionary")
    parser.add_argument("--test_data", type=str, help="Path to test data")
    parser.add_argument("--predictions", type=str, help="Path of predictions")

    args = parser.parse_args()

    log.debug("Predict started... arguments parsed successfully.")

    strategy = args.strategy
    temperature = args.temperature
    gpt_deployment_name = args.gpt_deployment_name
    prompt_config = args.prompt_config
    test_data = args.test_data
    prediction_path = args.predictions
    azure_openai_endpoint = args.azure_openai_endpoint
    azure_openai_api_key = args.azure_openai_api_key
    main(
        strategy,
        temperature,
        gpt_deployment_name,
        azure_openai_endpoint,
        azure_openai_api_key,
        prompt_config,
        test_data,
        prediction_path,
    )
