# How to test the initial setup your Model Factory with 

**Step 1.** In the development branch, supply an explicit value or accept the defaults in the file, config.yaml*. The pipelines uses multiple variables and they should be set for both 'pr' and 'dev' plus any additional environments. Also, set the variables for all models (i.e. nyc_taxi, london_taxi). The config.yaml file is split into the following sections, set the values in each section:

  - aml_config: Stores the configuration of azure resources hosting the Azure Machine Learning workspace.
  - environment_config: Stores the base image and dynamic properties set at runtime.
  - pipeline_configs: Stores the configuration for pr and dev pipelines for each model supported by the solution.
  - deploy_configs: Stores online and batch configuration for deployments for each model.  

# Azure DevOps Steps

**Step 1.** *Provision Infrastructure* - Execute the infrastructure provision pipeline (infra_provision_bicep_pipeline.yml OR infra_provision_terraform_pipeline.yml).

**Step 2.** *Run PR pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for build validation

**Step 3.** *Run CI pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for continuous integration.

# Github Workflows Steps

**Step 1.** *Provision Infrastructure* - Execute the infrastructure provision pipeline
- ModelFactory-Bicep-Deployment.yml
- ModelFactory-Terraform-Deployment.yml

**Step 2.** *Run PR pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for build validation
- nyc_taxi_pr_pipeline.yml
- london_taxi_pr_pipeline.yml

**Step 3.** *Run CI pipeline for a model of your choice* - Execute any of the Azure Pipelines created above for continuous integration.
- nyc_taxi_ci_pipeline.yml
- london_taxi_ci_pipeline.yml

# Extending the solution
See how_to_onboard_new_model.md