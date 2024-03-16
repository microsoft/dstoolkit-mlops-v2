# How to Onboard new model in dstoolkit-mlops pipelines

Welcome to the process of onboarding a new AI model to your Model Factory! The content here will guide you through all the necessary steps and provide detailed instructions for adding a new model to your factory's repertoire.

## Prerequisites

Before you begin the onboarding process, ensure you have the following prerequisites in place:

- **Model Factory Environment:** Your Model Factory environment should be set up and operational. This includes having the necessary infrastructure, libraries, and dependencies ready. Refer to setup document for setting up the model factory in your environment

- **New Model:** You should have the ML model you want to onboard. This is the custom model that you've developed.

## Steps to Onboard a New ML Model

Follow these steps to onboard a new ML model to your Model Factory:

## Set model execution properties in config.yaml file

The /config/config.yaml file contains a node for the following:

**Note: Unless you have modified variable names in either variable groups or github variables, leave all $(variables) unchanged.** 

- aml_config: Stores the configuration of azure resources hosting the Azure Machine Learning workspace.
- environment_config: Stores the base image and dynamic properties set at runtime.
- pipeline_configs: Stores the configuration for pr and dev pipelines for each model supported by the solution.
- deploy_configs: Stores online and batch configuration for deployments for each model.

### aml_config

Set the properties for this component in Azure Pipelines variable group of your Azure DevOps project or within Variables in your github repository:

- subscription_id: The subscription id in Azure hosting the Azure Machine Learning workspace.
- resource_group_name: The name of the resource group hosting the Azure Machine Learning workspace. 
- workspace_name: The name of the Azure Machine Learning workspace in which the models will be trained and served.

### environment config

Set the properties for the environment when executing build validation or continuous integration pipelines.  A note on base image selection. When choosing a base image for training and inferencing in Azure Machine Learning take into consideration compatibility with the libraries,  dependencies, and performance characteristics of your model. Also consider image maintainability, size, and licensing.

- env_base_image: Base image to be used for training and model execution


### pipeline configs

Start by copying an existing pipeline config and accepting the defaults or modifying the properties with values relevant for each model and environment:

- cluster_region: Azure region in which the AML compute cluster should be hosted.
- cluster_size: Set to an Azure VM Size according to the naming convention here: [Azure VM Sizes](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes).
- cluster_name: A string representing the name of the compute cluster.
- conda_path: The path within the solution to the conda file used to establish the dependencies needed by a given model.
- aml_env_name: A string denoting the name of a given environment for a given model.
- dataset_name: The name of the dataset used when training the model.

### deployment configs

Start by copying an existing deployment config and accepting the defaults or modifying the properties with values relevant for each model and serving method to be added (Follow the naming convention {_model name_}_{execution context "batch" or "online"}_{environment}"):

#### Config for batch deployment

- score_file_name: Name of the scoring file for the given model.
- score_dir: Directory within which the scoring file is stored.
- batch_cluster_name: The name of the compute cluster.
- batch_cluster_region: The name of the compute cluster.
- batch_cluster_size: Set to an Azure VM Size according to the naming convention here: [Azure VM Sizes](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes).
- deployment_conda_path: Path to the conda file to be used when serving the given model.
- endpoint_name: The name of the endpoint on which to serve the model. This has to be unique within region.
- endpoint_desc: A description of the endpoint serving the model.
- deployment_name:  A name for the deployment serving the model.
- cluster_instance_count: number of nodes in the cluster serving the model.
- max_concurrency_per_instance: Max concurrency setting for the cluster instances serving the model.
- mini_batch_size: An integer representing the batch size when serving the model.
- output_file_name: Name of the file in which the model output will be stored.
- max_retries: Number of retries in the event of failure while executing the model.
- deployment_base_image: Reference to the base image used in serving the model. A note on base image selection. When choosing the base image for inferencing take into consideration compatibility with the libraries, dependencies, and performance characteristics of your model. Also consider image maintainability, size, and licensing.
- deployment_desc: A description for the deployment serving the model.
- test_dataset_name: The name of a dataset to use when testing deployments of the model.

#### config for online deployment

- score_file_name: Name of the scoring file for the given model.
- test_file_path: Path to a json file containing a sample request to the online endpoint serving the model.
- endpoint_name: The name of the endpoint on which to serve the model. This has to be unique within region.
- endpoint_desc: A description of the endpoint serving the model.
- deployment_desc: A description for the deployment serving the model.
- deployment_name:  A name for the deployment serving the model.
- deployment_traffic_allocation: A number setting the traffic attribute for an online endpoint.
- deployment_vm_size: Set to an Azure VM Size according to the naming convention here: [Azure VM Sizes](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes).
- deployment_base_image: Reference to the base image used in serving the model. A note on base image selection. When choosing the base image for inferencing take into consideration compatibility with the libraries, dependencies, and performance characteristics of your model. Also consider image maintainability, size, and licensing.  
- deployment_conda_path: Path to the conda file to be used when serving the given model.
- score_dir: Directory within which the scoring file is stored.
- deployment_instance_count: number of nodes in the cluster serving the model.  

## Extend the src folder

The src folder contains one top level folder for each model. The name of the folder corresponds to the pipeline config and deployment config nodes in the /config/config.yaml file. For instance, the pipeline config node in the config.yaml file contains a node for "london_taxi_pr". Accordingly, there is a folder in /src called "london_taxi" that corresponds to the model name.  You can start by copying one of the existing {root}/src/model folders and pasting it in this folder.  Once copied, rename it to the model name of the new model, and modify the folders and files within the new folder according the steps required by the new model. 

Each sample usecase has steps for prep, transform, train, predict, score and register the model.  You can use the same steps or add or remove steps based on your specific usecase.
Common Steps to include:

- Data preparation : Noise Reduction, Missing Value Imputation, Inconsistencies Elimination
- Data Transform :  Data Normalization, Data Formatting, Data Aggregation.
- Training :  Train a machine learning model with the preprocessed data
- Prediction :  Use the trained machine learning model to make predictions
- Scoring : Evaluate the performance of the trained machine learning model on a test dataset
- Register : Save the trained machine learning model in the AML Model Registry.

## Extend the mlops folder

The mlops folder contains one top level folder for each model. The name of the folder corresponds to the pipeline config and deployment config nodes in the /config/config.yaml file. For instance, the pipeline config node in the config.yaml file contains a node for "london_taxi_pr". Accordingly, there is a folder in /mlops called "london_taxi" that corresponds to the model name. You can start by copying one of the existing model folders and pasting it in this folder.  Once copied, rename it to the model name of the new model, and modify the files within the new folder.  

There are multiple sub-folders in this folder. The following modifications should be made:

### mlops/{model}/components folder

- The components folder contains one yaml file for each step in the AzureML pipeline. Add additional yaml files for additional steps needed by the model generation process or remove any step not required. Modify each of the files for changes in inputs and outputs for the step.  Each of these yaml files refers to python code in src folder in the repo.  Update the inputs , outputs and function name in python command based on the function in the src folder. Remove, update or add files depending on the changes in the scripts in the src folder in the solution root.

### mlops/{model}/data

- If the new model requires batch inferencing, add a relevant dataset to the "data" folder to enable testing of the batch endpoint. 

### mlops/{model}/environment folder

- The environment folder contains the conda.yml file needed by the Model related to any python package dependencies. 

### mlops/{model}/src folder

- The src folder contains the mlops_pipeline.py file. This file contains the main AzureML pipeline code and should be modified if there are any changes in the components folder with regard to number of yaml files, or the inputs and outputs for those yaml files.
- Modify the model name referenced on line 1 of start_local_pipeline.py to correspond to the new model.

## Extend the model folder

The model folder contains one top level folder for each model. The name of the folder corresponds to the pipeline config and deployment config nodes in the /config/config.yaml file. For instance, the pipeline config node in the config.yaml file contains a node for "london_taxi_pr". Accordingly, there is a folder in /model called "london_taxi" that corresponds to the model name. You can start by copying one of the existing model folders and pasting it in this folder.  Once copied, rename it to the model name of the new model, and modify the files within the new folder. Depending on the serving model, remove either of the batch or online.

- Modify the conda.yml file in the batch_environment and/or online_environment folders as needed.
- Add test data for the new model to the batch_test_data and/or online_test_data folders as needed.

## test folder

The test folder contains one top level folder for each model. The name of the folder corresponds to the pipeline config and deployment config nodes in the /config/config.yaml file. For instance, the pipeline config node in the config.yaml file contains a node for "london_taxi_pr". Accordingly, there is a folder in /model called "london_taxi" that corresponds to the model name. You can start by copying one of the existing model folders and pasting it in this folder.  Once copied, rename it to the model name of the new model, and modify the files within the new folder. Depending on the serving model, remove either of the batch or online. Add any unit tests for the new ML Model should be stored in new folder.

## .azure-pipelines folder  

The .azure-pipelines folder contains a pr and a ci file for each model. There are two yaml pipelines per model in this folder. Add a new pair of files for the new model and make the following changes: 

- The include paths in trigger and pr section with values related to new ML Model.
- The default value for model_type parameter in parameters section.

## Implement a robust and scalable solution for data provisioning

When implementing model factory, use whichever method the team normally uses for making data available to models. Out-of-the-box, this solution uses data uploaded to AML according to the configuration file, config/data_config.json. **We recommend using this file only when testing the initial setup of the solution.**

## Test the new model

Having completed the steps above, you should now be able to run a test of the pr and ci builds for the new model.  Find/Fix bugs as needed until the pr and ci execute successfully.

- If using Azure pipelines, run the pipeline, register_data_assets.yml to upload data for the new model.
- If using github workflows, run the workflow , register_data_assets.yml to upload data for the new model.
- Upon check-in, the pr model should be triggered automatically.  If it is not triggered automatically, run the pipeline manually.
- Once the pr pipeline completes, execute the ci pipeline for the new model.
