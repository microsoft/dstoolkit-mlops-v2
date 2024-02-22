data "azurerm_client_config" "current" {} 
resource "azurerm_resource_group" "rg" {
  location            = var.location
  name = var.rg_name
  
}

resource "azurerm_application_insights" "aml_appins" {
  name                = "${var.appinsights_name}"
  location            = var.location
  resource_group_name = var.rg_name
  application_type    = "web"
  depends_on = [azurerm_resource_group.rg]
}

resource "azurerm_key_vault" "akv" {
  name                = "${var.keyvault_name}"
  location            = var.location
  resource_group_name = var.rg_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "premium"
  depends_on = [azurerm_resource_group.rg]
}

resource "azurerm_storage_account" "stacc" {
  name                     = "${var.storage_acct}"
  location                 = var.location
  resource_group_name      = var.rg_name
  account_tier             = "Standard"
  account_replication_type = "LRS"
  depends_on = [azurerm_resource_group.rg]
}

resource "azurerm_container_registry" "acr" {
  name                          = "${var.container_registry_name}"
  location                      = var.location
  resource_group_name           = var.rg_name
  sku                           = "Basic"
  admin_enabled                 = true
  depends_on = [azurerm_resource_group.rg]
  }

  resource "azurerm_machine_learning_workspace" "adl_mlw" {
  name                          = "${var.workspace_name}"
  location                      = var.location
  resource_group_name           = var.rg_name
  application_insights_id       = azurerm_application_insights.aml_appins.id
  key_vault_id                  = azurerm_key_vault.akv.id
  storage_account_id            = azurerm_storage_account.stacc.id
  container_registry_id         = azurerm_container_registry.acr.id
  public_network_access_enabled = true
  depends_on = [azurerm_resource_group.rg]
  identity {
    type = "SystemAssigned"
  }
}