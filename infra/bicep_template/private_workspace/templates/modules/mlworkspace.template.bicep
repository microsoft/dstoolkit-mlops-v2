@description('The location into which your Azure resources should be deployed.')
param location string

@description('Name of the storage resource.')
param storageAccount string

@description('Name of the key vault resource.')
param keyVaultName string

@description('Name of the application insights resource.')
param appInsightsName string

@description('Name of the container registry resource.')
param containerRegistryName string

@description('Name of the azure machine learning resource.')
param amlWorkspaceName string

resource stg 'Microsoft.Storage/storageAccounts@2022-09-01' existing = {
  name: storageAccount
}

resource kv 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: keyVaultName
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: containerRegistryName
}

resource workspace 'Microsoft.MachineLearningServices/workspaces@2023-04-01' = {
  name: amlWorkspaceName
  location: location
  dependsOn: [
    stg
    kv
    appInsights
    containerRegistry
  ]
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    keyVault: kv.id
    applicationInsights: appInsights.id
    containerRegistry: containerRegistry.id
    storageAccount: stg.id
    sku: 'enterprise'
  }
}
