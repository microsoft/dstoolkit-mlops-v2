# Introducing Model Factory

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

- docs/BranchingStrategy.md: Explains a recommended branching strategy.
- docs/FAQ.md: Contains a list of one or more frequently asked questions.
- docs/GeneralDocumentation.md: Provides guidance and recommended practices on MLOps in general.
- docs/GettingStarted.md: Explains the process for setting up your implementation of Model Factory.
- docs/InfrastructureDesign.md: Contains high-level visual representation of the infrastructure used in the solution.
- docs/OnboardingNewModel.md: Explains the procedure for adding a new model to the solution.
- docs/TestInitialSetup.md: Explains the procedure to follow to test the ability to deploy an infrastructure, run pr and ci builds.
- CONTRIBUTING.md: Explains the process for contributing to the project
- LICENSE.md: A standard License terms document.
- SECURITY.md: Explains procedure for raising security issues and vulnerabilities in this solution.

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

- (Option 1). VSCode dev container
  - Run the docker desktop daemon
    - Open repo in the [provided dev container](.devcontainer/devcontainer.json) in VSCode
      - Open VSCode terminal after the repo is opened in the dev container

- (Option 2). Create a local conda environment

  - Open the terminal and run the following commands to create a conda environment (we assume that anaconda has been installed on your local computer):

    - conda env create -name dstoolkit Python=3.9 # this does not work for some computers, the code could be conda create --name dstoolkit python=3.9
    - conda activate dstoolkit # if this doesn't work in your terminal, you can go to the Anaconda Navigator, click Environments, click dstoolkit and then hit the green play button and open terminal from there. 
    - pip install -r .devcontainer/requirements.txt

- Sign in with Azure CLI : run `az login -t <your tenant>`

- **Note**: Before running the training pipeline locally, you will have to have the data assets registered. If not already done, you can register the data using the following command:
  - `python -m mlops.common.register_data_asset --data_config_path config/data_config.json`
- Run the training pipeline under test using the module notation (for example, `python -m mlops.nyc_taxi.start_local_pipeline --build_environment pr --wait_for_completion True`)

## Caching Python Dependencies

**Caching** is used to store Python dependencies to improve build times by reusing packages between runs. The cache is managed using the [Cache@2](https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/cache-v2?view=azure-pipelines) task in the pipeline.

An example of how caching is implemented in this repo can be found in [build_validation_pipeline.yml](.azure-pipelines\templates\build_validation_pipeline.yml).

### Understanding Cache Key, Cache Path, and Restore Keys

- **Cache Key**: A unique key based on `python_build_validate`, the agent OS (`$(Agent.OS)`), and the `build_validation_requirements.txt` file.
  
  Example: 
  
``` bash
python_build_validate | "$(Agent.OS)" | .azure-pipelines/requirements/build_validation_requirements.txt`
```

- **Cache Path**: Dependencies are cached at `$(PIP_CACHE_DIR)`, where `pip` stores package files.

- **Restore Keys**: If an exact cache match isn’t found, the pipeline will attempt to restore based on partial keys: 

``` bash
python_build_validate | "$(Agent.OS)"`.
```

### Variables Used

- **`PIP_CACHE_DIR`**: Directory where `pip` stores cached package files.
- **`Agent.OS`**: The operating system of the build agent, used as part of the cache key.

## Running Debug Tasks in VS Code

You can use Visual Studio Code to run and debug specific tasks related to the MLOps pipelines. The following configurations are set up in the [launch.json](.vscode/launch.json) file, allowing you to execute various scripts with ease.

### Available Debug Tasks

1. **Register Data Asset**
   - **Command:** `python -m mlops.common.register_data_asset --data_config_path config/data_config.json`
   - **Description:** Registers a data asset using the provided configuration file.

2. **Start NYC Taxi Local Pipeline**
   - **Command:** `python -m mlops.nyc_taxi.start_local_pipeline --build_environment=<environment> --wait_for_completion=<True/False>`
   - **Description:** Starts the NYC Taxi pipeline in a local environment. You will be prompted to specify the `build_environment` and whether the pipeline should wait for completion.

3. **Start London Taxi Local Pipeline**
   - **Command:** `python -m mlops.london_taxi.start_local_pipeline --build_environment=<environment> --wait_for_completion=<True/False>`
   - **Description:** Starts the London Taxi pipeline in a local environment. You will be prompted to specify the `build_environment` and whether the pipeline should wait for completion.

### How to Run

1. Open the **Debug** panel in Visual Studio Code.
2. Select the desired debug task from the dropdown list. The options are:
   - `Register Data Asset`
   - `Start NYC Taxi Local Pipeline`
   - `Start London Taxi Local Pipeline`
3. Click the green play button (`▶`) next to the dropdown to start the task.
4. For the NYC Taxi and London Taxi pipelines, you will be prompted to enter two values:
   - **Build Environment:** Choose from `pr`, `dev`, or any other configured environments.
   - **Wait for Completion:** Choose `True` if you want the pipeline to wait for completion before exiting, or `False` to allow it to run asynchronously.
5. The output and any debugging information will be displayed in the **Debug Console** or **Integrated Terminal**, depending on the task configuration.

## Build Validation Policies for Azure Repos Git

### Limitation in Azure DevOps Pipelines

Azure Pipelines support PR triggers in YAML configuration when the repository is hosted on **GitHub**, but **not** when the repository is hosted on **Azure Repos Git**. In other words, using the `pr:` section in YAML files works for GitHub repos, but **will not** work for Azure Repos Git.

Example of a PR trigger that works in GitHub, but not in Azure Repos:

```yaml
pr:
  - master
  - develop
```

This limitation means that maintainers need to rely on [branch policies in Azure Repos Git](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser) to enforce build validation, rather than configuring this directly in the pipeline YAML file.

### Community Issue

The issue has been raised by the community, noting that Azure DevOps doesn’t support this PR trigger feature natively, which forces users to manage branch policies through the Azure DevOps UI rather than in YAML configuration. This presents an additional administrative burden as maintainers need to manage both YAML pipeline definitions and non-configuration-based policies.

The community issue and thread discussion can be found [here](https://developercommunity.visualstudio.com/t/pr-triggers-in-yaml-should-be-supported-on-azure-d/385329).

### Alternative: Branch Policies for Build Validation

To enforce build validation in Azure Repos, branch policies provide a robust alternative. These policies allow more configuration options and are essential for protecting branches with mandatory builds before merging pull requests.

Follow the steps outlined in the Azure DevOps [Branch Policies documentation](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser) to set up branch policies for build validation:

**Note**: You need to have appropriate [permissions](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser#prerequisites) to create Build Validation Policies.

1. Ensure you have created the Pipeline prior to creating the Build Validation Policy.

1. Navigate to Branch Policies:
    - Go to your Azure DevOps "Project Settings".
    - Navigate to Repos > Repositories.
    - Select the Repository from the list.
    - Select the "Policies" tab.
    - Find the "Branch Policies" section and select the branch you want to set the policy for (e.g., development).

1. Add Build Validation:
    - Under "Build validation", click "+" to add a build policy.
    - Select the pipeline you want to run when a PR is created or updated.
    - Configure the policy settings, such as requiring the build to pass before completing the PR.
    - Fill in the optional box for the paths (see the [Paths](#set-path-policies) section for more information).
    - Click "Save".

For more information about Build Validation Policies, please see the [documentation](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser#build-validation).

### Set Path Policies

Each policy contains a list of paths that specify which files or directories should trigger the pipeline when
changed. By defining these paths, we ensure that only the necessary pipelines are executed, reducing unnecessary builds and
tests, and speeding up the overall CI/CD process. For example:

- Changes to the `src/` directory trigger the build and validation pipeline.
- Changes to the `src/london_src/*` directory trigger the london_taxi pipelines and not the nyc_taxi or docker_taxi pipelines.

### Notes

- Ensure that your environment is correctly set up and all necessary dependencies are installed before running these tasks.
- The available options for `build_environment` and `wait_for_completion` are defined in the [launch.json](.vscode/launch.json) file and can be modified to suit your project’s needs.
- If you encounter any issues, check the [launch.json](.vscode/launch.json) file in the `.vscode` directory to verify the configuration.

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
