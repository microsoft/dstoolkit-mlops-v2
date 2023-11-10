# Configure the Microsoft Azure Provider
terraform {
  backend "azurerm" {}
}
provider "azurerm" {
  skip_provider_registration = "true"
  features {}
  
}