data "azurerm_client_config" "current" {}
resource "azurerm_resource_group" "aml_rg" {
  name     = "rg-aml-pri-${var.basename}-${var.project_code}-${var.version_num}"
  location = var.location
}

resource "azurerm_application_insights" "aml_appins" {
  name                = "aml-appins-${var.basename}-${var.project_code}-${var.version_num}"
  location            = azurerm_resource_group.aml_rg.location
  resource_group_name = azurerm_resource_group.aml_rg.name
  application_type    = "web"
}

resource "azurerm_key_vault" "akv" {
  name                = "akvaml${var.basename}${var.project_code}${var.version_num}"
  location            = azurerm_resource_group.aml_rg.location
  resource_group_name = azurerm_resource_group.aml_rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "premium"
}

resource "azurerm_storage_account" "stacc" {
  name                     = lower("staccaml${var.basename}${var.project_code}${var.version_num}")
  location                 = azurerm_resource_group.aml_rg.location
  resource_group_name      = azurerm_resource_group.aml_rg.name
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_machine_learning_workspace" "adl_mlw" {
  name                          = "mlw-${var.basename}-${var.project_code}-${var.version_num}"
  location                      = azurerm_resource_group.aml_rg.location
  resource_group_name           = azurerm_resource_group.aml_rg.name
  application_insights_id       = azurerm_application_insights.aml_appins.id
  key_vault_id                  = azurerm_key_vault.akv.id
  storage_account_id            = azurerm_storage_account.stacc.id
  public_network_access_enabled = false
  identity {
    type = "SystemAssigned"
  }

}
# Create Azure DNS Zone
resource "azurerm_dns_zone" "dns_zone" {
  name                = "dnszone${var.basename}.com"
  resource_group_name = azurerm_resource_group.aml_rg.name
}

# Create Azure Vitural Network
resource "azurerm_virtual_network" "aml_vnet" {
  name                = "aml-vnet-${var.basename}"
  location            = azurerm_resource_group.aml_rg.location
  resource_group_name = azurerm_resource_group.aml_rg.name
  address_space       = ["10.0.0.0/16"]
  dns_servers         = ["10.0.0.5"]
}

resource "azurerm_subnet" "amlsubnet" {
  name                                      = "dev-subnet"
  resource_group_name                       = azurerm_resource_group.aml_rg.name
  address_prefixes                          = ["10.0.1.0/24"]
  virtual_network_name                      = azurerm_virtual_network.aml_vnet.name
  private_endpoint_network_policies_enabled = true
}
# Create a private endpoint for Azure ML workspace
resource "azurerm_private_endpoint" "aml_pe" {
  name                = "aml-pe-${var.basename}"
  location            = azurerm_resource_group.aml_rg.location
  resource_group_name = azurerm_resource_group.aml_rg.name
  subnet_id           = azurerm_subnet.amlsubnet.id

  private_service_connection {
    name                           = "aml-pe-conn-${var.basename}"
    private_connection_resource_id = azurerm_machine_learning_workspace.adl_mlw.id
    is_manual_connection           = false
    subresource_names              = ["mlWorkspaces"]
  }
}