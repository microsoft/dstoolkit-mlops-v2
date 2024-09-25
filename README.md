# Introducing Model Factory

## About this repo

The idea of this template is to provide a minimum number of scripts to implement development environment to train new models using Azure ML SDK v2 With Azure DevOps or Github Actions.

The template contains the following folders/files:

- [.github](.github): the folder contains Github Workflow related files (yaml files to define the Builds).
- [.azure-pipelines](.azure-pipelines): the folder contains Azure DevOps related files (yaml files to define Builds).
- [docs](docs): documentation.
- [src](src): source code that is not related to Azure ML directly. Usually, there is data science related code.
- [mlops](mlops): scripts that are related to Azure ML.
- [mlops/london-taxi](mlops/london-taxi), [mlops/nyc-taxi](mlops/nyc-taxi), [mlops/docker_taxi](mlops/docker_taxi): fake pipelines with some basic code.
- [.amlignore](.amlignore): using this file we are removing all the folders and files that are not supposed to be in Azure ML compute.

The template contains the following documents:

- [docs/how-to/BranchingStrategy.md](docs/how-to/BranchingStrategy.md): Explains a recommended branching strategy.
- [docs/how-to/GettingStarted.md](docs/how-to/GettingStarted.md): Explains the process for setting up your implementation of Model Factory.
- [docs/how-to/InfrastructureDesign.md](docs/how-to/InfrastructureDesign.md): Contains high-level visual representation of the infrastructure used in the solution.
- [docs/how-to/OnboardingNewModel.md](docs/how-to/OnboardingNewModel.md): Explains the procedure for adding a new model to the solution.
- [docs/how-to/TestInitialSetup.md](docs/how-to/TestInitialSetup.md): Explains the procedure to follow to test the ability to deploy an infrastructure, run pr and ci builds.
- [docs/references/References.md](docs/references/References.md): Contains references and additional resources related to the project.
- [CONTRIBUTING.md](CONTRIBUTING.md): Explains the process for contributing to the project.
- [LICENSE.md](LICENSE.md): A standard License terms document.
- [SECURITY.md](SECURITY.md): Explains procedure for raising security issues and vulnerabilities in this solution.

## How to use the repo

Information about how to setup the repo is in [the following document](./docs/how-to/GettingStarted.md).

## Local Execution

You can start training pipelines from your local computer by creating an environment based on the following instructions:

- Rename .env.sample to .env and update .env file with values from your Azure subscription for the following properties (Any values that are already set can be left unchanged (BUILD_BUILDID="local"). This value is dynamic when run in the context of Azure DevOps or Github Actions, and used for various naming/tagging purposes.):
- SUBSCRIPTION_ID
- RESOURCE_GROUP_NAME
- WORKSPACE_NAME
- Check all parameters in [config.yaml](config/config.yaml) for the model under test.  **Note**: In the sample code provided in this solution, the development team elected to use a single config file, but this is by no means the only way to do this. It's possible to simplify configs by extracting elements common across all models into their own file, and to create model-specific configs in their own files.  The Class MLOPsConfig supports passing config_path in its constructor enabling a modular design for configuration. 
- Install [Azure Cli and Azure ML extensions](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli?view=azureml-api-2&tabs=public#installation)
- Create the an environment on your local machine using one of the following options below.

- (Option 1). VSCode base dev container
  - Run the docker desktop daemon
  - Open repo in VSCode
    - Open the Command Palette (Ctrl+Shift+P)
    - Select "Reopen in Container"
    - Choose the base dev container: "DSToolkit .devcontainer\base\devcontainer.json"
    - Open VSCode terminal after the repo is opened in the dev container

- (Option 2). Use the docker_taxi Dockerfile for the dev container
  - Run the docker desktop daemon
  - Open repo in VSCode
    - Open the Command Palette (Ctrl+Shift+P)
    - Select "Reopen in Container"
    - Choose the custom dev container: "DSToolkit-DockerTaxi .devcontainer\docker_taxi\devcontainer.json"
    - Open VSCode terminal after the repo is opened in the dev container

- (Option 3). Create a local conda environment

  - Open the terminal and run the following commands to create a conda environment (we assume that anaconda has been installed on your local computer):

    - conda env create -name dstoolkit Python=3.9 # this does not work for some computers, the code could be conda create --name dstoolkit python=3.9
    - conda activate dstoolkit # if this doesn't work in your terminal, you can go to the Anaconda Navigator, click Environments, click dstoolkit and then hit the green play button and open terminal from there. 
    - pip install -r .devcontainer/requirements.txt
- Sign in with Azure CLI : run `az login -t <your tenant>`

- **Note**: Before running the training pipeline locally, you will have to have the data assets registered. If not already done, you can register the data using the following command:
  - `python -m mlops.common.register_data_asset --data_config_path config/data_config.json`
- Run the training pipeline under test using the module notation (for example, `python -m mlops.nyc_taxi.start_local_pipeline --build_environment pr --wait_for_completion True`)

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
