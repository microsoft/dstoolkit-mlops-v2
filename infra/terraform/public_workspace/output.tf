output "client_id" {
  value = azurerm_user_assigned_identity.mlops_identity.client_id
}

output "tenant_id" {
  value = azurerm_user_assigned_identity.mlops_identity.tenant_id
}

output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  value = azurerm_storage_account.stacc.name
}

output "keyvault_name" {
  value = azurerm_key_vault.akv.name
}

output "container_registry_name" {
  value = azurerm_container_registry.acr.name
}
