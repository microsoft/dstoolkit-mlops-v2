data "azurerm_client_config" "current" {} 
resource "azurerm_application_insights" "aml_appins" {
  name                = "aml-ai-${var.basename}-${var.project_code}-${var.version_num}"
  location            = var.location
  resource_group_name = var.rg_name
  application_type    = "web"
}

resource "azurerm_key_vault" "akv" {
  name                = "akvaml${var.basename}${var.project_code}${var.version_num}"
  location            = var.location
  resource_group_name = var.rg_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "premium"
}

resource "azurerm_storage_account" "stacc" {
  name                     = lower("staccaml${var.basename}${var.project_code}${var.version_num}")
  location                 = var.location
  resource_group_name      = var.rg_name
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_container_registry" "acr" {
  name                          = "cr${var.basename}${var.project_code}${var.version_num}"
  location                      = var.location
  resource_group_name           = var.rg_name
  sku                           = "Basic"
  admin_enabled                 = true
  }

  resource "azurerm_machine_learning_workspace" "adl_mlw" {
  name                          = "mlw-${var.basename}-${var.project_code}-${var.version_num}"
  location                      = var.location
  resource_group_name           = var.rg_name
  application_insights_id       = azurerm_application_insights.aml_appins.id
  key_vault_id                  = azurerm_key_vault.akv.id
  storage_account_id            = azurerm_storage_account.stacc.id
  container_registry_id         = azurerm_container_registry.acr.id
  public_network_access_enabled = true
  identity {
    type = "SystemAssigned"
  }
}