# DSToolkit MLOps V2 Refresh

## About this repo

The idea of this template is to provide a minimum number of scripts to implement development environment to train new models using Azure ML SDK v2 With Azure DevOps or Github Actions.

The template contains the following folders/files:

- .github: the folder contains Github Workflow related files(yaml files to define the Builds).
- .azure-pipelines: the folder contains Azure DevOps related files (yaml files to define Builds).
- docs: documentation.
- src: source code that is not related to Azure ML directly. Usually, there is data science related code.
- mlops: scripts that are related to Azure ML.
- mlops/london-taxi, mlops/nyc-taxi: fake pipelines with some basic code.
- .amlignore: using this file we are removing all the folders and files that are not supposed to be in Azure ML compute.

The template contains the following documents:

- docs/how_to_setup.md: explain how to configure the template.

## How to use the repo

Information about how to setup the repo is in [the following document](./docs/how_to_setup.md).

## Local Execution
You can start training pipelines from a local computer creating an environment based on the following instructions:

- Rename .env.sample to .env and update .env file with parameters from your Azure subscription
- Check all parameters in [config.yaml](config/config.yaml)
- Install [Azure Cli and Azure ML extensions](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli?view=azureml-api-2&tabs=public#installation)
- Create the local environment using one of the following options below.
- (Option 1). VSCode dev container

    - Run the docker desktop daemon
    - Open repo in the [provided dev container](.devcontainer/devcontainer.json) in VSCode
    - Open VSCode terminal after the repo is opened in the dev container

- (Option 2). Create a local conda environment

    -  Open the terminal and run the following commands to create conda environment (we assume that anaconda has been installed on the local computer):

        - conda env create -name dstoolkit Python=3.9
        - conda activate dstoolkit
        - pip install -r .devcontainer/requirements.txt

- Sign in with Azure CLI : run `az login -t <your tenant>`
- Run a desired training pipeline using the module notation (for example, `python -m mlops.nyc_taxi.start_local_pipeline --build_environment pr --wait_for_completion True`)


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
