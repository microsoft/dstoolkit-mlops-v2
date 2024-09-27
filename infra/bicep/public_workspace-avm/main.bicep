targetScope = 'subscription'

@description('The resource group into which your Azure resources should be deployed.')
param resourceGroupName string

@description('The location into which your Azure resources should be deployed.')
param location string

@description('Name of the storage resource.')
param storageAccount string

@description('The type of storage account that should be deployed.')
param sku string = 'Standard_LRS'

@description('The type of storage account that should be deployed.')
param kind string = 'StorageV2'

@description('The storage access tier at which the storage account should be deployed.')
param accessTier string = 'Hot'

@description('Name of the key vault resource.')
param keyVaultName string

@description('Name of the application insightes resource.')
param appInsightsName string

@description('Name of the container registry resource.')
param containerRegistryName string

@description('Name of the container registry resource.')
param amlWorkspaceName string

resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: resourceGroupName
  location: location
  tags: {}
}

// storage
module stg 'br/public:avm/res/storage/storage-account:0.9.1' = {
  scope: resourceGroup(rg.name)
  name: storageAccount
  params: {
    name: storageAccount
  }
}

// key vault
module kv 'br/public:avm/res/key-vault/vault:0.9.0' = {
  scope: resourceGroup(rg.name)
  name: keyVaultName
  params: {
    name: keyVaultName
  }
}

// application insights
module appInsightsResource 'br/public:avm/res/insights/component:0.4.1' = {
  scope: resourceGroup(rg.name)
  name: appInsightsName
  params: {
    name: appInsightsName
    workspaceResourceId: 
  }
}

// container registry
 module containerRegistryResource 'br/public:avm/res/container-registry/registry:0.5.1' = {
  scope: resourceGroup(rg.name)
  name: containerRegistryName
  params: {
    name: containerRegistryName
  }
 }

 // azure machine learning
 module mlworkspace 'br/public:avm/res/machine-learning-services/workspace:0.8.0' = {
  scope: resourceGroup(rg.name)
  name: amlWorkspaceName
  params: {
    name: amlWorkspaceName
    sku: 
  }
 }
