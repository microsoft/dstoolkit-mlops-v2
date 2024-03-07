# Testing the initial setup 

**Step 1.** In the development branch, supply an explicit value or accept the defaults in the file, config/config.yaml. The pipelines uses multiple variables and they should be set for both 'pr' and 'dev' plus any additional environments. Also, set the variables for all models (i.e. nyc_taxi, london_taxi). The config.yaml file is split into the following sections, set the values in each section:

  - aml_config: Stores the configuration of azure resources hosting the Azure Machine Learning workspace.
  - environment_config: Stores the base image and dynamic properties set at runtime.
  - pipeline_configs: Stores the configuration for pr and dev pipelines for each model supported by the solution.
  - deploy_configs: Stores online and batch configuration for deployments for each model.  

## Azure DevOps Steps

**Step 1.** *Provision Infrastructure* - Execute the infrastructure provisioning pipeline (infra_provision_bicep_pipeline.yml OR infra_provision_terraform_pipeline.yml).

- .azure-pipelines/infra/bicep/infra_provision_bicep.yml
- .azure-pipelines/infra/bicep/infra_provision_terraform.yml

**Step 2.** *Run PR pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for build validation

- .azure-pipelines/nyc_taxi_pr_pipeline.yml
- .azure-pipelines/london_taxi_pr_pipeline.yml

**Step 3.** *Run CI pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for continuous integration.

- .azure-pipelines/nyc_taxi_ci_pipeline.yml
- .azure-pipelines/london_taxi_ci_pipeline.yml

## Github Workflows Steps

**Step 1.** *Provision Infrastructure* - Execute the infrastructure provision pipeline

- .github/workflows/ModelFactory-Bicep-Deployment.yml
- .github/workflows/ModelFactory-Terraform-Deployment.yml

**Step 2.** *Run PR pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for build validation

- .github/workflows/nyc_taxi_pr_pipeline.yml
- .github/workflows/london_taxi_pr_pipeline.yml

**Step 3.** *Run CI pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for continuous integration.

- .github/workflows/nyc_taxi_ci_pipeline.yml
- .github/workflows/london_taxi_ci_pipeline.yml

## Extending the solution

Once you can confidently build the infrastructure and run a pr and ci build for a model, you are ready to add your own use cases to the Model Factory. See [Onboarding a New Model](./OnboardingNewModel.md)
