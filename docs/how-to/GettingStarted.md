# Getting started with Model Factory

This solution supports Azure Machine Learning (ML) as a platform for ML, and GitHub Actions as the platform for operationalization. MLOps with Model Factory provides automation of the following:

* Infrastructure provisioning using GitHub workflows with either Bicep or Terraform as the IaC language.
* A CI build triggered upon changes to one or more models.
* A CD build and deployment of one or more models to batch and online endpoints.

**Note:** Azure Pipelines support is deprecated and will be removed after 2026-01-31. All pipelines have triggers disabled. GitHub Actions is the supported CI/CD path.

## Assumptions

* The user of this guide understands basic operations on GitHub, Visual Studio Code, or an IDE of their choice. Use the following guide to familiarize yourself with GitHub [Getting started with your GitHub account](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account). Use the following guide to familiarize yourself with Visual Studio Code [Visual Studio Code documentation](https://code.visualstudio.com/docs)

* Your team has an Azure Subscription within which to host Model Factory. If you don't have an Azure subscription, create a free account  by following this link. [Free Azure Subscription](https://azure.microsoft.com/en-us/free/search/?ef_id=_k_67e7bdd2a501151df8d8d83b02edc75b_k_&OCID=AIDcmm5edswduu_SEM__k_67e7bdd2a501151df8d8d83b02edc75b_k_&msclkid=67e7bdd2a501151df8d8d83b02edc75b)

* You have created a service principal with workload identity federation configured for GitHub Actions to operate the infrastructure and run AML build and CD workflows. Follow the instructions on this page to setup federated credentials: [Use GitHub Actions to connect to Azure](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure?tabs=azure-portal%2Cwindows#add-federated-credentials). Create one federated credential using Pull Request as entity type, and one using Branch as entity type and specifying the root branch in your repository.

* You have granted the service principal above, at least Contributor, and User Access Administrator on the target subscription in Azure.

## Setup your source control environment

**Step 1.** Clone the repository, create a *main* branch, and make it the default branch so that all PRs merge to it. This guide assumes that the team works with a *main* branch as the primary source for coding and improving model quality. Later, you can implement GitHub workflows to move code from the *main* branch to qa/main or that executes a release process with each check-in. However, release management is not in scope of this guide.

## Azure DevOps Setup (DEPRECATED - For Reference Only)

**⚠️ DEPRECATED:** Azure Pipelines support is deprecated and will be removed after 2026-01-31. All pipeline triggers are disabled. Use the GitHub Workflows Setup section below for active CI/CD.

This section is retained for historical reference only. For new deployments, skip directly to the "GitHub Workflows Setup" section below.

## GitHub Workflows Setup

**Step 1.** If you are starting fresh and do not need Azure Pipelines for reference, delete the .azure-pipelines directory.

**Step 2.** Add the following variables in Settings > Secrets and Variables > Variables:

> ⚠️ Some Azure resource names have to be unique within your Azure subscription or region. Please make sure to use unique names. One strategy is to append a three-part version to the names defined in the variables below (e.g., for AML workspace, you might use "aml-mlw-001").

**Mandatory Infrastructure variables for Bicep and Terraform provisioning:**

* APPINSIGHTS_NAME: A string compliant with the naming convention for an Azure Application Insights resource. Must be unique.
* ARM_CLIENT_ID: The application (client) ID of the service principal created for GitHub Actions authentication.
* ARM_TENANT_ID: The tenant ID corresponding to the service principal.
* AZURE_RM_SVC_CONNECTION: The service connection name (for compatibility with existing config).
* CONTAINER_REGISTRY_NAME: A string compliant with the naming convention for an Azure Container Registry resource. Must be unique.
* KEYVAULT_NAME: A string compliant with the naming convention for an Azure Key Vault resource. Must be unique.
* LOCATION: A valid Azure region name (e.g., "eastus", "westeurope").
* RESOURCE_GROUP_NAME: A string compliant with the naming convention for an Azure resource group. Must be unique within subscription.
* STORAGE_ACCT_NAME: A unique alphanumeric string (3-24 characters, lowercase) for an Azure storage account.
* SUBSCRIPTION_ID: The GUID for the Azure subscription hosting the Azure Machine Learning workspace.
* WORKSPACE_NAME: A string compliant with the naming convention for an Azure Machine Learning workspace resource. Must be unique.

**Terraform-only variables:**

* TFSTATE_RESOURCE_GROUP_NAME: Resource group name for storing Terraform state files. Must be unique within subscription.
* TFSTATE_STORAGE_ACCT_NAME: Unique alphanumeric storage account name (3-24 characters, lowercase) for Terraform state files.

**Model Deployment Variables:**

**Note:** Models may be deployed to batch endpoints, online endpoints, or both by setting the properties below. When both are configured to True, the CD workflow will execute to both endpoints simultaneously.

* IS_BATCH_DEPLOYMENT: Set to "True" to deploy models to a batch endpoint, or "False" to skip batch deployment.
* IS_ONLINE_DEPLOYMENT: Set to "True" to deploy models to an online endpoint, or "False" to skip online deployment.

**Step 3.** Ensure this GitHub repository has proper [workflow and access permissions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository#about-github-actions-permissions-for-your-repository):
- Go to Settings > Actions > General
- Under "Workflow permissions", select "Read and write permissions"
- Check "Allow GitHub Actions to create and approve pull requests" if needed

**Step 4.** Use the boolean variable `is_docker` in your GitHub workflows to determine if unit tests need Docker. Set `is_docker` to "true" if tests require Docker, otherwise set to "false".

Once you have completed this setup, test your configuration by running an end-to-end test that includes all the steps detailed in [Testing the Initial Setup](./TestInitialSetup.md)
