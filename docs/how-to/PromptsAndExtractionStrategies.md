# Prompts and Extraction Strategies

This document describes how to configure prompts and extraction strategies for the invoice_processing example.

## Hyperparameters

The LLM's temperature can be modified through the [`experiment_config.yaml](config/experiment_config.yaml).

```yaml
predict_config:
  strategy: gpt_only
  gpt_deployment_name: gpt-4o
  temperature: 0
  
```

## Strategies

The predict component in the experimentation framework can support multiple extraction strategies. Strategies are defined in [this folder](/src/invoice_processing/predict_component/predict/data_extraction).
The [predict.py](/src/invoice_processing/predict_component/predict/predict.py) chooses which strategy to use according to the definitions in the [experiment_config.yaml](/config/experiment_config.yaml) file, as seen below:

``` yaml
predict_config:
  strategy: gpt_only
  gpt_deployment_name: gpt-4o
  ...
```

Currently, the experimentation framework has only one strategy [GPT Only](/src/invoice_processing/predict_component/predict/data_extraction/extractors/gpt_only_extractor.py), defined and implemented.
The strategy parses the images as `.png`, `.jpg` or `.jpeg` to GPT model which provides an answer as `.json`. Different model deployment name can be specified in the same configuration file with `gpt_deployment_name`. Azure OpenAI API key and endpoint have to be set in `.env` to use this strategy.

### Add a new strategy

To add a new strategy for the images:

1. In [extractors folder](/src/invoice_processing/predict_component/predict/data_extraction/extractors) add a new file with your class implementing [base_extractor.py](/src/invoice_processing/predict_component/predict/data_extraction/extractors/base_extractor.py), similar to [gpt_only_extractor.py](/src/invoice_processing/predict_component/predict/data_extraction/extractors/gpt_only_extractor.py)
1. Load the new strategy as part of the factory, add your new strategy in function `load_default_extractors` located at the [data_extractor_factory.py](/src/invoice_processing/predict_component/predict/data_extraction/data_extractor_factory.py)

## Cost estimation

The estimated cost is calculated by the `estimate_cost` function within [`predict.py`](/src/invoice_processing/predict_component/predict/predict.py). The values are hard coded based on [this documentation](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/?msockid=068db13b7d9c6c9a095ca4127cb76d73#pricing) and East US 2 region and need to be configured for any new model (or model in a new region) you want to run in the AML pipeline.

## Prompts

Prompts for data extraction from images are defined in `prompts/templates` folder as jinja files. The prompt is then loaded using the [`PromptManager`](/src/invoice_processing/predict_component/predict/data_extraction/prompts/prompt_manager.py) from the [`experiment_config.yaml`](/config/experiment_config.yaml) file as follows (the [example](/src/invoice_processing/predict_component/predict/data_extraction/extractors/gpt_only_extractor.py) is from the GPT only extractor):

```python
user_prompt = PromptManager.get_prompt(
        self.config["prompt_name"],
    line_item_instructions=self.config["line_item_instructions"],
    structure={json.dumps(structure)}
)
```

```yaml
predict_config:
  ...
  prompt_config:
    prompt_name: medical_claim_reimbursement
    line_item_instructions: complex
```

The experiment will use [medical_claim_reimbursement.j2](../../src/invoice_processing/predict_component/predict/data_extraction/prompts/templates/medical_claim_reimbursement.j2) as the prompt provided to the LLM.

### Add a new prompt

To add a new prompt, create a new jinja file within the [prompts/templates](/src/invoice_processing/predict_component/predict/data_extraction/prompts/templates/) folder. If you add a variable or another required input, these will need to be added within the [`experiment_config.yaml` file](/config/experiment_config.yaml) and where the prompt is loaded within each strategy.

For example, let's imagine I created a prompt called `pharmacy_charges_claims.j2` as follows:

``` jinja
### Instructions ###
As a Pharmacy Charges Claim Reimbursement Processor, your primary responsibility involves examination of the provided pharmacy receipt in order to accurately extract key information necessary for reimbursement procedures.

### Required Details ###
- Provider's Name
- Final Charges
{% if additional_fields == 'client_name' %}
- Client's Name 
{% endif %}
```

I will need to change the [`experiment_config.yaml` file](/config/experiment_config.yaml) as follows:

```yaml
predict_config:
  ...
  prompt_config:
    prompt_name: pharmacy_charges_claims
    additional_fields: client_name
```

and the [GPT only extractor](/src/invoice_processing/predict_component/predict/data_extraction/extractors/gpt_only_extractor.py) as follows:

```python
user_prompt = PromptManager.get_prompt(
        self.config["prompt_name"],
    additional_fields=self.config["additional_fields"],
    structure={json.dumps(structure)}
)
```

**Note:** If you are **NOT** using any additional variables within your prompt, remember to remove unnecessary parameters from [`experiment_config.yaml` file](/config/experiment_config.yaml) and [GPT only extractor](/src/invoice_processing/predict_component/predict/data_extraction/extractors/gpt_only_extractor.py):

```yaml
predict_config:
  ...
  prompt_config:
    prompt_name: pharmacy_charges_claims
```

```python
user_prompt = PromptManager.get_prompt(
        self.config["prompt_name"],
    structure={json.dumps(structure)}
)
```

For more information on Jinja, check out [their documentation](https://jinja.palletsprojects.com/en/stable/).
