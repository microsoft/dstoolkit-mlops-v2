# Getting started with Model Factory

This solution supports Azure Machine Learning (ML) as a platform for ML, and Azure DevOps or github as a platform for operationalization. MLOps with Model Factory provides automation of the following:

* Infrastructure provisioning using either Azure Pipelines or github workflows.
* A PR build triggered upon changes to one or more models.
* A CI build and deployment of one or more models to batch and online endpoints.

# Assumptions: 
- The user of this guide understands basic operations on github.com, visual studio code, or an ide of their choice. Use the following guide to familiarize yourself with github [Getting started with your GitHub account](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account). Use the following guide to familiarize yourself with visual studio code [Visual Studio Code documentation](https://code.visualstudio.com/docs)
- An Azure Subscription. If you don't have an Azure subscription, create a free account before you begin.
- You have created an app registration to create the infrastructure, and operate the pipelines.  Grant the service principal, at least Contributor, and User Access Administrator on the target subscription in Azure.
**Use this document as a reference to create an app registration: [Create a Microsoft Entra application and service principal that can access resources](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal)

To get started with Model Factory, complete the steps below. 

# Setup your source control environment.
**Step 1.** Clone the repository, create a *development* branch, and make it the default branch so that all PRs merge to it. This guide assumes that the team works with a *development* branch as the primary source for coding and improving model quality. Later, you can implement an Azure Pipeline to move code from the *development* branch to qa/main or that executes a release process with each check-in. However, release management is not in scope of this guide. 

# Azure DevOps Setup:
**Step 1.** Delete the .github directory.

**Step 2.** Create an Azure DevOps organization and project. Follow the instructions here: [Create a project in Azure DevOps](https://learn.microsoft.com/en-us/azure/devops/organizations/projects/create-project?view=azure-devops&tabs=browser) 

**Step 3.** Create a new variable group named **"mlops_platform_dev_vg"**, add the variables and their values listed below: 
Information about variable groups in Azure DevOps can be found in [Add & use variable groups](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=classic).
**Note To provision test or production infrastructure create a new variable group, add the required variables, and modify the reference to the variable group in either infra_provision_bicep_pipeline.yml or infra_provision_terraform_pipeline.yml files.**

**Mandatory Infrastructure variables for bicep and terraform provisioning.** 
- "APPINSIGHTS_NAME": Set to a value of your choosing.  Note the value must be unique.
- "AZURE_RM_SVC_CONNECTION":  Set to the name of the service connection created above. 
- "CONTAINER_REGISTRY_NAME": Set to a value of your choosing.  Note the value must be unique.
- "KEYVAULT_NAME": Set to a value of your choosing.  Note the value must be unique.
- "LOCATION": Set to valid value for the "Name" property for Azure Region.
- "RESOURCE_GROUP_NAME": Set to a value of your choosing.  Note the value must be unique.
- "STORAGE_ACCT_NAME": Set to an unique alphanumeric value of your choosing.
- "SUBSCRIPTION_ID": Set to the subscription id for the subscription hosting the Azure Machine Learning workspace.    
- "WORKSPACE_NAME": Set to a value of your choosing.  Note the value must be unique.

**Terraform only variables** 
- "TFSTATE_RESOURCE_GROUP_NAME": Set to an unique value of your choosing.
- "TFSTATE_STORAGE_ACCT_NAME": Set to an unique alphanumeric value of your choosing.

**Model Deployment Variables**
- "IS_BATCH_DEPLOYMENT" - Set to True to deploy models to a batch endpoint.
- "IS_ONLINE_DEPLOYMENT" - Set to True to deploy models to an online Endpoint.

**Step 4.** Create Azure Pipelines to deploy the infrastructure, and operate model builds and continuous integration.
Details about how to create a basic Azure Pipeline can be found in [Create your first pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline?view=azure-devops&tabs).

**Step 5.** Using the instructions above, if needed, create an azure pipeline to deploy the infrastructure using either the bicep (*.azure-pipelines/infra/bicep/infra_provision_bicep_pipeline.yml*) or terraform (*.azure-pipelines/infra/terraform/infra_provision_terraform_pipeline.yml*) yaml files. 

**Step 6.** Using the instructions above, if needed, create one or more Azure Pipelines to setup build validation for either or both of the use cases listed below:
- nyc_taxi
- london_taxi

**Step 7.** Using the instructions above, if needed, create one or more Azure Pipelines to setup continuous integration for either or both of the use cases listed below:
- nyc_taxi
- london_taxi

# GitHub Workflows Setup:
**Step 1.** Delete the .azurepipelines directory

**Step 2.** Add the following variables in Settings > Secrets and Variables > Variables:
  - APPINSIGHTS_NAME: A string compliant with the naming convention for an azure application insights resource.
  - ARM_CLIENT_ID: The application id corresponding to the service principal backing the service connection created above.
  - ARM_TENANT_ID: The tenant id corresponding to the service principal backing the service connection created above.
  - AZURE_RM_SVC_CONNECTION: The service connection name.
  - CONTAINER_REGISTRY_NAME: A string compliant with the naming convention for an azure container registry resource.
  - IS_BATCH_DEPLOYMENT: A boolean indicating whether to create a batch deployment when executing a given model's ci pipeline.
  - IS_ONLINE_DEPLOYMENT: A boolean indicating whether to create on online deployment when executing a given model's ci pipeline.
  - KEYVAULT_NAME: A string compliant with the naming convention for an azure key vault resource.
  - LOCATION: A string compliant with the naming convention for an azure region short name.
  - RESOURCE_GROUP_NAME: A string compliant with the naming convention for an azure resource group resource.
  - STORAGE_ACCT_NAME: A string compliant with the naming convention for an azure storage account resource.
  - SUBSCRIPTION_ID: A guid for the azure subscription hosting the azure machine learning workspace. 
  - TFSTATE_RESOURCE_GROUP_NAME: A string compliant with the naming convention for an azure resource group resource. The tfstate resource group hosts a storage account for storing the tfstate file produced when using terraform infrastructure provisioning.
  - TFSTATE_STORAGE_ACCT_NAME: A string compliant with the naming convention for an azure storage account resource. The tfstate storage account for storing the tfstate file produced when using terraform infrastructure provisioning.
  - WORKSPACE_NAME: A string compliant with the naming convention for an azure machine learning workspace resource. 

**Step 3.** Add the following secrets in Settings > Secrets and Variables > Secrets:
- ARM_CLIENT_SECRET: The is the client secret for the service principal backing the service connection created above.
- AZURE_CREDENTIALS: This secret is in the form below:

    ```
    {
    "clientId": "<GUID>",
    "clientSecret": "<PrincipalSecret>",
    "subscriptionId": "<GUID>",
    "tenantId": "<GUID>"
    }
    ```
