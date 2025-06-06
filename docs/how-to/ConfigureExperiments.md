# Configure Repository

This document describes how to configure the repository when running experiments.

## .env File

Before running any experiments, the user must create an empty file (`.env`) and copy  [.env_sample](../../.env.sample) into the created file. This file contains the environment variables required to connect to AML as well as Azure OpenAI credentials. The file will contain secrets and should therefore not be pushed to the repo.

```yaml
SUBSCRIPTION_ID=""
RESOURCE_GROUP_NAME=""
WORKSPACE_NAME=""
BUILD_BUILDID="local"
VNET_NAME=""
SUBNET_NAME=""
USER_ASSIGNED_IDENTITY_RESOURCE_ID=""
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_ENDPOINT=""
```

- subscription_id: The subscription id in Azure hosting the Azure Machine Learning workspace.
- resource_group_name: The name of the resource group hosting the Azure Machine Learning workspace.
- workspace_name: The name of the Azure Machine Learning workspace in which the models will be trained and served.
- vnet_name: The name of the existing virtual network for compute deployment.
- subnet_name: The name of the existing subnet for compute deployment.
- user_assigned_identity_resource_id: The resource id of the user assigned identity to assign to the compute instance. Formatted as "`/subscriptions/<sub-id\>/resourcegroups/<rg-name\>/providers/Microsoft.Manag

To download the `SUBSCRIPTION_ID`, `RESOURCE_GROUP_NAME` and `WORKSPACE_NAME`:

1. Sign in to AML studio
1. In the upper right Azure Machine Learning studio toolbar, select your workspace name
1. Select the Download config file link
1. Copy the relevant information from the file

To find the `VNET_NAME` and `SUBNET_NAME`:

1. go to the Azure Machine Learning studio
1. Select `Compute` on the left panel
1. Copy the information into the relevant fields

To find the OpenAI credentials, go to the Azure AI Foundary.

## config Folder

The [config folder](/config) contains three configuration files:

- [`config.yml`](/config/config.yaml) - configuration for Azure Machine Learning (AML) and the pipelines,
- [`experiment_config.yml`](/config/experiment_config.yaml) - experiment configurations,
- [`data_config.json`](/config/data_config.json) -  configuration for registering data sets in AML from local.

### `experiment_config.yml` file

This file is only used by the invoice_processing pipeline and is used to configure the experiment that will be run in AML. It contains the parameters for data preparation, prediction, and evaluation steps of the pipeline.

The file has several sections, each section configures a different component of the experiment.

The `experiment_description` section enables the users to add more information about the experiment they are about to run. The user can provide their user name, give a title to the experiment and explain what hypothesis is being tested in this experiment. This information will be logged into AML's job description.

``` yaml
experiment_description: 
  user_name: <USER_NAME>
  title: <EXPERIMENT_TITLE>
  hypothesis:  <EXPERIMENT_HYPOTHESIS>
```

Providing this information will make it easier to differentiate between the different AML runs.

The next section in the config file configures the data preparation step of the pipeline.

```yaml
prep_config:
  samples_amount: 4
  sampling_seed: 42
```

Adjust the `sample_amount` to be the number of samples on which you would like to run the pipeline (setting this value to zero means running on the entire data set).

Adjust the `sampling_seed` if you would like the sample to be reproducible in future experiments (otherwise set it to be -1)

Next, configure the prediction step:

```yaml
predict_config:
  strategy: gpt_only
  gpt_deployment_name: gpt-4o
  temperature: 0
  prompt_config:
    prompt_name: medical_claim_reimbursement_implicit_dates
    line_item_instructions: complex
```

See the [Prompt and Extraction Strategies](./PromptsAndExtractionStrategies.md) for more details.

Lastly, to configure the evaluation step:

```yaml
score_config:
  fuzzy_match_config:
    field_match_threshold: 0.0
  exact_match_fields:
    start_date_match: true
    end_date_match: true
    amount_match: true
  find_best_matches_strategy: levenshtein
  matchers_dict:
    serviceStartDate: date_exact_match
    serviceEndDate: date_exact_match
    amount: amount_exact_match
    description: description_levenshtein
```

### `data_config.json` file

The `data_config.json` file is used when registering a new data asset in AML.

```yaml
"DATA_PURPOSE": "test_data",
"DATA_PATH": "mlops/invoice_processing/data/raw_data",
"DATASET_NAME": "invoice_processing_test",
"DATASET_DESC": "this dataset is for pr validation only"
```

`DATA_PURPOSE`: what is the purpose of the dataset?

`DATA_PATH`: the local or Azure path from which to upload the data e.g. "azureml://subscriptions/<sub-id>/resourcegroups/<rg-name>/workspaces/<aml-name>/datastores/<blob-name>/paths/<path>"

`DATASET_NAME`: the name of the registered data asset

`DATASET_DESC`: description of the dataset

After configuring the parameters run:

```bash
python -m mlops.common.register_data_asset --data_config_path=<path_to_data_config_json_file>
```

The script will register the dataset in AML under data assets.

### `config.yaml` file

The [`/config/config.yaml`](/config/config.yaml) file contains a few sections, configuring different aspects of the AML pipeline.

`aml_config`: the following values are extracted from the `.env` file (do not modify or replace values in this section!).

```yaml
aml_config:
  subscription_id: ${SUBSCRIPTION_ID}
  resource_group_name: ${RESOURCE_GROUP_NAME}
  workspace_name: ${WORKSPACE_NAME}
  vnet_name: ${VNET_NAME}
  subnet_name: ${SUBNET_NAME}
  user_assigned_identity_resource_id: ${USER_ASSIGNED_IDENTITY_RESOURCE_ID}
```

`environment_configuration`: Set the properties for the environment when executing build validation or continuous integration pipelines. When choosing a base image for training and inferencing in Azure Machine Learning take into consideration compatibility with the libraries,  dependencies, and performance characteristics of your model. Also consider image maintainability, size, and licensing.

- env_base_image: Base image to be used for training and model execution
- build_reference: Name of the build to run in AML, by default will be `local`
- env_version: Env version to load. If -1, the latest version is loaded

```yaml
environment_configuration:
  env_base_image: mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04
  build_reference: ${BUILD_BUILDID}
  env_version: -1
```

`pipeline_configs`: Stores the configuration for ci and dev pipelines for each model supported by the solution.

- cluster_region: Azure region in which the AML compute cluster should be hosted.
- cluster_size: Set to an Azure VM Size according to the naming convention here: [Azure VM Sizes](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes).
- cluster_name: A string representing the name of the compute cluster.
- conda_path: The path within the solution to the conda file used to establish the dependencies needed by a given model. (Optional if using `dockerfile_path` and `docker_context_path`)
- aml_env_name: A string denoting the name of a given environment for a given model.
- dataset_name: The name of the data asset which contains the images we want to extract data from.
- gt_name: The name of the data asset which contains the corresponding ground truth (manually annotated image extractions).

**Important note:** If you would like to use a different dataset for your experiments, please modify the invoice_processing_dev and leave invoice_processing_pr as-is to enable quick PR validation.

```yaml
pipeline_configs:
  invoice_processing_pr:
    cluster_region: eastus
    cluster_size: STANDARD_DS3_v2
    cluster_name: cpucluster
    conda_path: mlops/invoice_processing/environment/conda.yml
    aml_env_name: invoice_processing_env
    dataset_name: invoice_processing_test
    gt_name: invoice_processing_test_gt

  invoice_processing_dev:
    cluster_region: eastus
    cluster_size: STANDARD_DS3_v2
    cluster_name: cpucluster
    conda_path: mlops/invoice_processing/environment/conda.yml
    aml_env_name: invoice_processing_env
    dataset_name: validated_gt_images
    gt_name: validated_gt_annotations
```

`invoice_processing_pr` is for the CI pipeline, and runs the pipeline on a small dataset. `invoice_processing_dev` is used in development mode.
The choice between running in pr or dev mode is configured in [start_local_pipeline.py](../../mlops/invoice_processing/start_local_pipeline.py):

```python
mlops_pipeline.prepare_and_execute("invoice_processing", "pr", "True", None, None)
```

`deployment_configs`: Stores online and batch configuration for deployments for each model.
