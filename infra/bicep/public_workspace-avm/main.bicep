targetScope = 'subscription'

@description('The resource group into which your Azure resources should be deployed.')
param rg string

@description('The location into which your Azure resources should be deployed.')
param location string

@description('Name of the storage resource.')
param storageAccount string

@description('The type of storage account that should be deployed.')
param storageAccountSku string = 'Standard_LRS'

@description('The type of storage account that should be deployed.')
param storageAccountKind string = 'StorageV2'

@description('The storage access tier at which the storage account should be deployed.')
param storageAccountAccessTier string = 'Hot'

@description('Name of the key vault resource.')
param keyVault string

@description('Name of the application insightes resource.')
param appInsights string

@description('Name of the container registry resource.')
param containerRegistry string

@description('Name of the container registry resource.')
param amlWorkspace string

@description('Create mode of the key vault resource.')
param keyVaultCreateMode string = 'default'


// resource group
// https://github.com/Azure/bicep-registry-modules/blob/avm/res/resources/resource-group/0.4.0/avm/res/resources/resource-group/README.md
module resource_group 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: rg
  params: {
    name: rg
    location: location
  }
}

// storage
// https://github.com/Azure/bicep-registry-modules/blob/avm/res/storage/storage-account/0.9.1/avm/res/storage/storage-account/README.md
// param accountType string
module storege_account 'br/public:avm/res/storage/storage-account:0.9.1' = {
  scope: resourceGroup(resource_group.name)
  name: storageAccount
  params: {
    name: storageAccount
    location: location
    skuName: storageAccountSku
    kind: storageAccountKind
    accessTier: storageAccountAccessTier
    supportsHttpsTrafficOnly: true
  }
}

// key vault
// https://github.com/Azure/bicep-registry-modules/blob/avm/res/key-vault/vault/0.9.0/avm/res/key-vault/vault/README.md
module key_vault 'br/public:avm/res/key-vault/vault:0.9.0' = {
  scope: resourceGroup(resource_group.name)
  name: keyVault
  params: {
    name: keyVault
    location: location
    sku: 'standard'
    createMode: keyVaultCreateMode
    enableVaultForDeployment: true
  }
}

// application insights
// https://github.com/Azure/bicep-registry-modules/blob/avm/res/insights/component/0.4.1/avm/res/insights/component/README.md
module application_insights 'br/public:avm/res/insights/component:0.4.1' = {
  scope: resourceGroup(resource_group.name)
  name: appInsights
  params: {
    name: appInsights
    workspaceResourceId: resourceId(resource_group.name,log_analytics_workspace.name)

    location: location
    kind: 'web'
    applicationType: 'web'
  }
}

// log analytics
// https://github.com/Azure/bicep-registry-modules/blob/avm/res/operational-insights/workspace/0.7.0/avm/res/operational-insights/workspace/README.md
module log_analytics_workspace 'br/public:avm/res/operational-insights/workspace:0.7.0' = {
  scope: resourceGroup(resource_group.name)
  name: 'la'
  params: {
    name: 'la'
  }
}
// container registry
// https://github.com/Azure/bicep-registry-modules/blob/avm/res/container-registry/registry/0.5.1/avm/res/container-registry/registry/README.md
module azure_container_registry 'br/public:avm/res/container-registry/registry:0.5.1' = {
  scope: resourceGroup(resource_group.name)
  name: containerRegistry
  params: {
    name: containerRegistry
    location: location
    acrSku: 'Basic'
    acrAdminUserEnabled: true
  }
}

 // azure machine learning
//  https://github.com/Azure/bicep-registry-modules/blob/avm/res/machine-learning-services/workspace/0.8.0/avm/res/machine-learning-services/workspace/README.md
module maching_learning_workspace 'br/public:avm/res/machine-learning-services/workspace:0.8.0' = {
  scope: resourceGroup(resource_group.name)
  name: amlWorkspace
  params: {
    name: amlWorkspace
    location: location
    sku: 'Basic'
    managedIdentities: {
      systemAssigned: true
    }
    associatedKeyVaultResourceId: resourceId(resource_group.name,key_vault.name)
    associatedStorageAccountResourceId: resourceId(resource_group.name,storege_account.name)
    associatedApplicationInsightsResourceId: resourceId(resource_group.name,application_insights.name)
    associatedContainerRegistryResourceId: resourceId(resource_group.name,azure_container_registry.name)
  }
}
