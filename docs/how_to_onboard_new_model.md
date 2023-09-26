# How to Onboard new model in dstoolkit-mlops pipelines

Welcome to the process of onboarding a new AI model to your Model Factory! The content here will guide you through all the necessary steps and provide detailed instructions for adding a new model to your factory's repertoire.

## Prerequisites

Before you begin the onboarding process, ensure you have the following prerequisites in place:

**Model Factory Environment:** Your Model Factory environment should be set up and operational. This includes having the necessary infrastructure, libraries, and dependencies ready. Refer to setup document for setting up the model factory in the environment

**New Model:** You should have the AI model you want to onboard. This is the custom model that you've developed.

## Steps to Onboard a New AI Model

Follow these steps to onboard a new AI model to your Model Factory:

**Model Configuration:** The model_config.json file in config folder contains a section for each environment and model in the repository. The "ML_MODEL_CONFIG_NAME" element is used internally to semantically refer to the model through-out. The "ENV_NAME" element refers to the environment for the ML Model. e.g. pr, dev, test and prod.

You can start by copying an existing model section and modify it with relevant values. Provide valid values for all the configuration elements for your model.


**Azure DevOps Pipeline folder:** The devops/pipeline folder contains one top level folder for each model. The name of the folder should match the "ML_MODEL_CONFIG_NAME" element in model_config.json file. You can start by copying one of an existing folder in this folder and modify the files within the new folder. Rename the new folder and files within with "ML_MODEL_CONFIG_NAME" element value in model_config.json file. 

There are two yaml pipelines in this folder - pr and ci. Both should be modified to reflect using the new AI Model.
The modification in these files include:
- The include paths in trigger and pr section with values related to new AI Model.
- The default value for model_type parameter in parameters section.

**mlops folder:** The mlops folder contains one top level folder for each model. The name of the folder should match the "ML_MODEL_CONFIG_NAME" element in model_config.json file. You can start by copying one of an existing model folder in this folder and modify the files within the new folder. Rename the new model folder with "ML_MODEL_CONFIG_NAME" element value in model_config.json file. 

There are multiple sub-folders in this folder. The following modifications should be executed:
- Remove the batch_test_data folder if batch endpoints are not required for the new model. In case, the new model is related to batch inferencing, add relevant dataset to represent testing the batch endpoint using this dataset.
- The components folder contains one yaml file for each step in AzureML pipeline. Add additional yaml files for additional steps needed by the model generation process or remove any step not required. Modify each of the files for changes in inputs and outputs for the step. Each of these yaml files refers tio python code in src folder in the repo. Any changes to inputs and output will impact the corresponding python files as well.
- The configs folder contains the deployment and data configuration for the Model. The data_config.json file contains one element for each type of dataset required. For example, london_taxi model has 3 datasets - "pr_data", "batch_test_data" and "training_data" represented by the "data_purpose" element. Remove batch_test_data if it is not required however, both pr_data and training_data are important for the Model generation. The deployment sub-folder contains two files - batch_config.json and realtime_config.json. These contain deployment related configuration. Modify the values in these configuration files to reflect your Model deployment. Remove batch_config.json file if Model is not related to batch inferencing.
- The data folder contains data that would be uploaded to AzureML data assets.
- The envvironment folder contains conda.yml file needed by the Model related to any python package dependencies. 
- The src folder contains the mlops_pipeline.py file. This contains the main AzureML pipeline code and should be modified if there is any changes in the components folder with regard to number of yaml files, the inputs and outputs for those yaml files.

**Model folder:** The mlops folder contains one top level folder for each model. The name of the folder should match the "ML_MODEL_CONFIG_NAME" element in model_config.json file. You can start by copying one of an existing model folder in this folder and modify the files within the new folder. Rename the new model folder with "ML_MODEL_CONFIG_NAME" element value in model_config.json file. Provide a new sample-request.json file with data that can test the Model after deployment on AzureML.


**src folder:** The mlops folder contains one top level folder for each model. The name of the folder should match the "ML_MODEL_CONFIG_NAME" element in model_config.json file. You can start by copying one of an existing model folder in this folder and modify the files within the new folder. Rename the new model folder with "ML_MODEL_CONFIG_NAME" element value in model_config.json file. The python code related to AzureML pipeline should be stored in this folder. Remove, update or add files depending on the changes in the components folder discussed earlier. 

**test folder:** The test folder contains one top level folder for each model. The name of the folder should match the "ML_MODEL_CONFIG_NAME" element in model_config.json file. You can start by copying one of an existing model folder in this folder and modify the files within the new folder. Rename the new model folder with "ML_MODEL_CONFIG_NAME" element value in model_config.json file. The unit tests for the ML Model should be stored in this folder
