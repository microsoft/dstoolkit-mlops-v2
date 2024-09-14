output "storage_account_name" {
  value = azurerm_storage_account.stacc.name
}

output "container_registry_name" {
  value = azurerm_container_registry.acr.name
}

output "appinsights_name" {
  value = azurerm_application_insights.aml_appins.name
}

output "keyvault_name" {
  value = azurerm_key_vault.akv.name
}

output "workspace_name" {
  value = azurerm_machine_learning_workspace.adl_mlw.name
}

output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "location" {
  value = var.location
}
