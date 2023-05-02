# MLOps Model Factory Accelerator

> **Note:**
> This is a repo that can be shared to our customers. This means it's NOT OK to include Microsoft confidential
> content. All discussions should be appropriate for a public audience.

MLOps Model Factory is a platform and an end to end workflow that supports generating multiple models and used for deployment to any target. 

## Features

- Supports generation of multiple ML Models through a single platform and repo
- MLOps pipeline for Data preparation, transformation, Model Training, evaluation, scoring and registration 
- Based on Azure ML SDK v2 1.4
- Option to package ML Models in Docker Images



## About this repo

The idea of this platform and end to end workflow is to provide a minimum number of scripts to implement an environment to train and test multiple ML Models using Azure ML SDK v2 and Azure DevOps.

The workflow contains the following folders/files:

- devops: the folder contains Azure DevOps related files (yaml files to define Builds).
- docs: documentation.
- src: source code that is not related to Azure ML directly. This is typically data science related code.
- mlops: scripts that are related to Azure ML.
- mlops/nyc-taxi: a fake pipeline with some basic code to build a model
- mlops/london-taxi: a fake pipeline with some basic code to build another model
- test: a folder with dummy test to write unit tests for the build
- model: Model related files and dependencies

- .amlignore: using this file we are removing all the folders and files that are not supposed to be in Azure ML compute.

The workflow contains the following documents:

- docs/how_to_setup.md: explain how to configure the workflow.

## How to use the repo

Information about how to setup the repo is in [the following document](./docs/how_to_setup.md).  

## Reference

* [Azure Machine learning](https://docs.microsoft.com/azure/machine-learning)
* [Azure DevOps pipelines](https://learn.microsoft.com/en-gb/azure/devops/pipelines/)
* [Azure Machine learning SDK V2](https://learn.microsoft.com/en-gb/python/api/overview/azure/ai-ml-readme?view=azure-python)
* [Azure AD Service Principal](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
* [Azure Key Vault](https://learn.microsoft.com/en-gb/azure/key-vault/general/)