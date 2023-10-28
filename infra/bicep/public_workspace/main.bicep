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
module stg './modules/storage.template.bicep' = {
  name: storageAccount
  scope: resourceGroup(rg.name)
  params:{
    storageAccountName: storageAccount
    location: rg.location
    kind: kind
    accessTier: accessTier
    accountType: sku
  }
}

// key vault
module kv './modules/keyvault.template.bicep' = {
  name: keyVaultName
  scope: resourceGroup(rg.name)
  params: {
    keyVaultName: keyVaultName
    location: rg.location
  }
}

// application insights
module appInsightsResource './modules/appinsights.template.bicep' = {
  name:appInsightsName
  scope: resourceGroup(rg.name)
  params: {
    appInsightsName: appInsightsName
    location: rg.location
  }
}

// container registry
 module containerRegistryResource './modules/containerregistry.template.bicep' = {
  name: containerRegistryName
  scope: resourceGroup(rg.name)
  params: {
    containerRegistryName: containerRegistryName
    location: rg.location
  }
 }

 // azure machine learning
 module mlworkspace './modules/mlworkspace.template.bicep' = {
  name: amlWorkspaceName
  scope: resourceGroup(rg.name)
  params: {
    amlWorkspaceName: amlWorkspaceName
    storageAccount: stg.name
    keyVaultName: kv.name
    appInsightsName: appInsightsResource.name
    containerRegistryName: containerRegistryResource.name
    location: rg.location
  }
}
