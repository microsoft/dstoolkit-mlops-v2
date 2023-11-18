# How to setup your Model Factory with Azure DevOps

This template supports Azure Machine Learning (ML) as a platform for ML, and Azure DevOps as a platform for operationalization. MLOps with Model Factory provides automation of the following:

* Infrastructure provisioning
* A PR build triggered upon changes to one or more models
* A CI build and deployment of one or more models to batch and real-time endpoints.

## Prerequisites
- The user of this guide understands basic operations on github.com, visual studio code, or an ide of their choice. Use the following guide to familiarize yourself with github [Getting started with your GitHub account](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account). Use the following guide to familiarize yourself with visual studio code [Visual Studio Code documentation](https://code.visualstudio.com/docs)
- An Azure Subscription. If you don't have an Azure subscription, create a free account before you begin.
- Azure DevOps organization and project. Follow the instructions here: [Create a project in Azure DevOps](https://learn.microsoft.com/en-us/azure/devops/organizations/projects/create-project?view=azure-devops&tabs=browser) 
- You have setup an app registration, granted the resulting service principal, at least Contributor, and User Access Administrator on the target subscription.
**Use this document as a reference: [Create a Microsoft Entra application and service principal that can access resources](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal)

## Steps

**Step 1.** Create a service connection. Review [Manage service connections](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml) for instructions. 

Launch the Service Connection Wizard ![image](https://github.com/microsoft/dstoolkit-mlops-v2/assets/15255737/fb1aa33f-0299-4aa0-a0de-02dba4f8e919)

![image](https://github.com/microsoft/dstoolkit-mlops-v2/assets/15255737/32e6b323-289a-4030-a628-52261eefe58a) <br>**Use the Azure Resource Manager as service connection type**</br>    

![image](https://github.com/microsoft/dstoolkit-mlops-v2/assets/15255737/4dbb36fa-6511-442f-9e6e-bb805a68f827)<br>**Use the Manual option when creating the service connection**</br> 
    

**Step 2.** Create a new variable group named **"mlops_platform_dev_vg"**, add "AZURE_RM_SVC_CONNECTION" variable with the name of the service connection created above. 
Information about variable groups in Azure DevOps can be found in [Add & use variable groups](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=classic).

**Step 3.** Clone the repository, create a *development* branch, and make it the default branch so that all PRs merge to it. This guide assumes that the team works with a *development* branch as the primary source for coding and improving model quality. Later, you can implement an Azure Pipeline to move code from the *development* branch to qa/main or that executes a release process with each check-in. However, release management is not in scope of this guide.

### Set the configuration for provisioning the Model Factory Infrastructure

**Step 4.** In the development branch, for the properties below, supply a value or accept the defaults in the file, *infra_config.json*:
**Note: It is important to set a unique version number to avoid errors that result by deploying resources having the same names as ones that already exist.**
- **NAMESPACE:** Set a base name.
- **PROJECTCODE:** Set a project code.
- **VERSION:** Set a three-digit version string (zero-padded) to uniqueify azure resource names.
- **AZURE_RM_SVC_CONNECTION:** Set this to the name of the service connection created above.
- **RESOURCE_GROUP_NAME:** Set the name of a resource group into which azure resources will be deployed.
- **CLUSTER_NAME:** Set the name of the compute resource to be used by Model Factory for training, and deployments.
- **BATCH_CLUSTER_NAME:** Set the name of the compute resource to be used for batch inferencing.

**Step 5.** In the development branch, for the properties below, supply a value or accept the defaults in the file, *model_config.json*. The pipeline uses multiple variables and they should be set for both 'pr' and 'dev' plus any additional environments. Also, set the variables for all models (i.e. nyc_taxi, london_taxi)

- **ML_MODEL_CONFIG_NAME:** The unique model name used internally by the pipelines.
- **ENV_NAME:** The name of the environment. e.g pr, dev, test, prod.
- **CLUSTER_REGION:** The Azure location/region where the cluster should be created.
- **CONDA_PATH:** The location of the conda file (mlops/nyc_taxi/environment/conda.yml).
- **DISPLAY_BASE_NAME:** The run base name (see EXPERIMENT_BASE_NAME for details).
- **ENV_BASE_IMAGE_NAME:** The base image for the environment (ex.: mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04).
- **ENVIRONMENT_NAME:** A name for the Azure ML environment.
- **EXPERIMENT_BASE_NAME:** An experiment base name. This parameter as well as two more parameters below are used to form unique names for experiments, runs and models. You can find a rule for the names implemented as powershell code in [here](../devops/pipeline/templates/variables_template.yml). By default we are using the branch name as well as build id to form the names that helps us to differentiate experiments, runs and models when working on a large team of data scientists and software engineers. The EXPERIMENT_TYPE variable from the template is hard coded in *_dev_pipeline.yml files.
- **MODEL_BASE_NAME:** A model base name (see EXPERIMENT_BASE_NAME for details).
- **BATCH_DEPLOYMENT_CONFIG:** A relative path to the *batch_config.json* file.
- **REALTIME_DEPLOYMENT_CONFIG:** A relative path to the *realtime_config.json* file.
- **DATA_CONFIG_PATH:** relative path to the *data_config.json*.

**Step 6.**  In all *batch_config.json* and *realtime_config.json* files for each model, provide a unique name for the following properties:
- **BATCH_CLUSTER_NAME:** The unique name for a cluster to be used for batch inferencing. **Note: Since this cluster is created by the Infrastructure deployment, the name must match the value for BATCH_CLUSTER_NAME in */config/infra_config.yml* **
- **ENDPOINT_NAME:** The unique name for a batch or real-time endpoint.
- **DEPLOYMENT_NAME** The unique name for a batch or real-time deployment.

### Create Azure Pipelines to deploy the infrastructure, and operate model builds and continuous integration.
Details about how to create a basic Azure Pipeline can be found in [Create your first pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline?view=azure-devops&tabs).

**Step 7.** Using the instructions above, if needed, create an azure pipeline to deploy the infrastructure using either the bicep (*devops/pipeline/infra/bicep/infra_provision_bicep_pipeline.yml*) or terraform (*devops/pipeline/infra/terraform/infra_provision_terraform_pipeline.yml*) yaml files. 

**Step 8.** Using the instructions above, if needed, create one or more Azure Pipelines to setup build validation for either or both of the use cases listed below:
- nyc_taxi_pr_dev_pipeline.yml
- london_taxi_pr_dev_pipeline.yml

**Step 9.** Using the instructions above, if needed, create one or more Azure Pipelines to setup continuous integration for either or both of the use cases listed below:
- nyc_taxi_ci_dev_pipeline.yml
- london_taxi_ci_dev_pipeline.yml

**Step 10.** Setup a branch policy for the *development* branch. At this stage we have one or more Azure Pipeline(s) that should be executed on every PR to the *development* branch. At the same time successful completion of the build is not a requirement when files not affecting operation of the model are changed. Set up the the *Path filter* field in the policy to respond to changes in same set of paths specified in the *_pr_dev_pipeline.yml files.
More details about how to create a policy can be found [Branch policies and settings](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser).

**Step 11. (Optional)** It's a common practice to execute a training job on the full dataset once a PR has been merged into the development branch. At the same time, the training process can take a long time (many hours or even days) and Azure DevOps agent will not be able to report on the status of the training job due to timeout settings. So, it's very hard to implement a single CI Build that will wait for a new model (training results) and execute the remaining steps after model approval, model movement promotion to a qa environment, and eventual model deployment etc.

Azure ML provides a solution that allows us to implement a *server* task in Azure DevOps Build and wait for the result of the pipeline training job with no Azure DevOps agent holding. Thanks to that it's possible to wait for results any amount of time and execute all other steps right after completion of the Azure ML training job. As for now, the feature is in active development, but you can [visit this link](https://github.com/Azure/azure-mlops-automation) to check the status and find how to get access. This new Azure ML feature can be included in your CI Build thanks to the extension that Azure ML team built or you can use RestAPITask for a direct REST call. In this template we implemented a version with the extension.


## Execute Pipelines

**Step 12.** *Provision Infrastructure* - Execute the infrastructure provision pipeline (infra_provision_bicep_pipeline.yml OR infra_provision_terraform_pipeline.yml).

**Step 13.** *Run PR pipeline* - Execute any of the Azure Pipelines created above for build validation

**Step 14.** *Run CI pipeline* - Execute any of the Azure Pipelines created above for continuous integration
