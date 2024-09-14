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


# resource "azurerm_user_assigned_identity" "mlops_identity" {
#   location            = var.location
#   name                = "mlopsv2-testing-umi"
#   resource_group_name = var.rg_name
# }
data "azurerm_user_assigned_identity" "mlops_identity" {
  name                = "mlopsv2-testing-auth"
  resource_group_name = var.rg_name
}

resource "azurerm_role_assignment" "mlops_identity_role" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Contributor"
  principal_id         = data.azurerm_user_assigned_identity.mlops_identity.principal_id
}

resource "azurerm_federated_identity_credential" "github_federated_credential" {
  name                = "github-federated-credential"
  resource_group_name = var.rg_name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  parent_id           = data.azurerm_user_assigned_identity.mlops_identity.id
  subject             = "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main"
}