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
If you prefer scripting the service principal creation, then follow the steps below:

## Create Azure service principal

Create an Azure service principal for the purpose of working with this repository. You can add more depending on number of environments you want to work on (Dev or Prod or Both). Service principals can be created using cloud shell, bash, PowerShell or from Azure UI. If your subscription is a part of an organization with multiple tenants, ensure that the Service Principal has access across tenants. 

1. Copy the following bash commands to your computer and update the **spname** (of your choice) and **subscriptionId** variables with the values for your project. This command will also grant the **Owner** role to the service principal in the subscription provided. This is required for Azure DevOps Pipelines and GitHub Actions to properly create and use resources in that subscription. 

    ``` bash
    spname="<your sp name>"
    roleName="Owner"
    subscriptionId="<subscription Id>"
    servicePrincipalName="Azure-ARM-${spname}"

    # Verify the ID of the active subscription
    echo "Using subscription ID $subscriptionID"
    echo "Creating SP for RBAC with name $servicePrincipalName, with role $roleName and in scopes     /subscriptions/$subscriptionId"
    
    az ad sp create-for-rbac --name $servicePrincipalName --role $roleName --scopes /subscriptions/$subscriptionId --sdk-auth 
    
    echo "Please ensure that the information created here is properly saved for future use."

1. Copy your edited commands into the Azure Shell and run them (**Ctrl** + **Shift** + **v**). If executing the commands on local machine, ensure Azure CLI is installed and successfully able to access after executing `az login` command. Azure CLI can be installed using information available [How to install the Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

1. After running these commands, you'll be presented with information related to the service principal. 

    ```json

      {
      "clientId": "<service principal client id>",  
      "clientSecret": "<service principal client secret>",
      "subscriptionId": "<Azure subscription id>",  
      "tenantId": "<Azure tenant id>",
      "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
      "resourceManagerEndpointUrl": "https://management.azure.com/", 
      "activeDirectoryGraphResourceId": "https://graph.windows.net/", 
      "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
      "galleryEndpointUrl": "https://gallery.azure.com/",
      "managementEndpointUrl": "https://management.core.windows.net/" 
      }
    ```

1. Copy the output, braces included. Save this information to a safe location, you'll need it later when setting the configuration for infrastructure provisioning and model operations.

1. Close the Cloud Shell once the service principal is created.
   
## Steps

**Step 1.** Create a service connection. Review [Manage service connections](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml) for instructions. 

Launch the Service Connection Wizard ![image](https://github.com/microsoft/dstoolkit-mlops-v2/assets/15255737/fb1aa33f-0299-4aa0-a0de-02dba4f8e919)

![image](https://github.com/microsoft/dstoolkit-mlops-v2/assets/15255737/32e6b323-289a-4030-a628-52261eefe58a) <br>**Use the Azure Resource Manager as service connection type**</br>    

![image](https://github.com/microsoft/dstoolkit-mlops-v2/assets/15255737/4dbb36fa-6511-442f-9e6e-bb805a68f827)<br>**Choose the Service principal (manual) radio button, enter the required subscription, name, etc details making sure to use the service principal created above in the ensuing dialog.**</br> 
    

**Step 2.** Create a new variable group named **"mlops_platform_dev_vg"**, add the following variables: 
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

**Terraform only variables ** 
  - "TFSTATE_RESOURCE_GROUP_NAME": Set to an unique value of your choosing.
  - "TFSTATE_STORAGE_ACCT_NAME": Set to an unique alphanumeric value of your choosing.

**Model Deployment Variables**
  - "IS_BATCH_DEPLOYMENT" - Set to True to deploy models to a batch endpoint.
  - "IS_ONLINE_DEPLOYMENT" - Set to True to deploy models to an online Endpoint.

**Step 3.** Clone the repository, create a *development* branch, and make it the default branch so that all PRs merge to it. This guide assumes that the team works with a *development* branch as the primary source for coding and improving model quality. Later, you can implement an Azure Pipeline to move code from the *development* branch to qa/main or that executes a release process with each check-in. However, release management is not in scope of this guide.

**Step 4.** In the development branch, supply an explicit value or accept the defaults in the file, config.yaml*. The pipelines uses multiple variables and they should be set for both 'pr' and 'dev' plus any additional environments. Also, set the variables for all models (i.e. nyc_taxi, london_taxi). The config.yaml file is split into the following sections:

  - aml_config - Stores the configuration of azure resources hosting the Azure Machine Learning workspace.
  - environment_config - Stores the base image and dynamic properties set at runtime.
  - pipeline_configs: - Stores the configuration for pr and dev pipelines for each model supported by the solution.
  - deploy_configs: - Stores online and batch configuration for deployments for each model.  


### Create Azure Pipelines to deploy the infrastructure, and operate model builds and continuous integration.
Details about how to create a basic Azure Pipeline can be found in [Create your first pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline?view=azure-devops&tabs).

**Step 5.** Using the instructions above, if needed, create an azure pipeline to deploy the infrastructure using either the bicep (*.azure-pipelines/infra/bicep/infra_provision_bicep_pipeline.yml*) or terraform (*.azure-pipelines/infra/terraform/infra_provision_terraform_pipeline.yml*) yaml files. 

**Step 6.** Using the instructions above, if needed, create one or more Azure Pipelines to setup build validation for either or both of the use cases listed below:
- nyc_taxi
- london_taxi

**Step 7.** Using the instructions above, if needed, create one or more Azure Pipelines to setup continuous integration for either or both of the use cases listed below:
- nyc_taxi
- london_taxi

**Step 8.** Setup a branch policy for the *development* branch. At this stage we have one or more Azure Pipeline(s) that should be executed on every PR to the *development* branch. At the same time successful completion of the build is not a requirement when files not affecting operation of the model are changed. Set up the the *Path filter* field in the policy to respond to changes in same set of paths specified in the *_pr_dev_pipeline.yml files.
More details about how to create a policy can be found [Branch policies and settings](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser).

## Execute the pipelines as needed

**Step 9.** *Provision Infrastructure* - Execute the infrastructure provision pipeline (infra_provision_bicep_pipeline.yml OR infra_provision_terraform_pipeline.yml).

**Step 10.** *Run PR pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for build validation

**Step 11.** *Run CI pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for continuous integration.
