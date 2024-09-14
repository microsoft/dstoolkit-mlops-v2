output "client_id" {
  value = azurerm_user_assigned_identity.mlops_identity.client_id
}

output "tenant_id" {
  value = azurerm_user_assigned_identity.mlops_identity.tenant_id
}

output "storage_account_name" {
  value = azurerm_storage_account.stacc.name
}

output "key_vault_name" {
  value = azurerm_key_vault.akv.name
}

output "container_registry_name" {
  value = azurerm_container_registry.acr.name
}

output "app_insights_name" {
  value = azurerm_application_insights.aml_appins.name
}

output "workspace_name" {
  value = azurerm_machine_learning_workspace.adl_mlw.name
}
