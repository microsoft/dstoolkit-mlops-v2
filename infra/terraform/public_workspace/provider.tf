# Configure the Microsoft Azure Provider
  terraform {
    backend "azurerm" {      
      use_oidc             = true  # Can also be set via `ARM_USE_OIDC` environment variable.}

    } 
}
  provider "azurerm" {
    
    use_oidc = true
    skip_provider_registration = "true"
    features {}
    
  }