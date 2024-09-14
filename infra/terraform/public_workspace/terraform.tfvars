appinsights_name = vat.appinsights_name
container_registry_name = var.container_registry_name
keyvault_name = var.keyvault_name
location = "#{LOCATION}#"
rg_name                = var.rg_name
storage_acct           = var.storage_acct
tfstate_rg_name        = "#{TFSTATE_RESOURCE_GROUP_NAME}#"  
tfstate_storage_acct   = "#{TFSTATE_STORAGE_ACCT_NAME}#"
workspace_name =        var.workspace_name
github_org             = var.github_org
github_repo            = var.github_repo

# appinsights_name = "#{APPINSIGHTS_NAME}#"
# container_registry_name = "#{CONTAINER_REGISTRY_NAME}#"
# keyvault_name = "#{KEYVAULT_NAME}#"
# location = "#{LOCATION}#"
# rg_name = "#{RESOURCE_GROUP_NAME}#"
# storage_acct = "#{STORAGE_ACCT_NAME}#" 
# tfstate_rg_name = "#{TFSTATE_RESOURCE_GROUP_NAME}#"  
# tfstate_storage_acct = "#{TFSTATE_STORAGE_ACCT_NAME}#"
# workspace_name = "#{WORKSPACE_NAME}#"
# github_org             = "#{GITHUB_ORG}#"
# github_repo            = "#{GITHUB_REPO}#"