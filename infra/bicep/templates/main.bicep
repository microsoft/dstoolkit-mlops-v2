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

@description('Boolean indicating whether to deploy a private endpoint and the related resources')
param requiresPrivateWorkspace bool=false

// default value is undefined string unless requiresPrivateWorkspace is true

@description('Name of the vnet resource.')
param virtualNetworkName string = 'undefined' 

@description('Name of the private dns zone resource.')
param privateDnsZoneName string = 'undefined' 

@description('Name of the private dns zone link resource.')
param privateDnsZoneLinkName string = 'undefined'

@description('Name of the private dns zone group resource.')
param privateDnsZoneGroupName string = 'undefined'

@description('Name of the private endpoint resource.')
param privateEndpointName string = 'undefined'

//var resourceGroupIdUniqueified = substring(uniqueString(resourceGroup().id),0,7)
//var storageAccountNameUniqueified = substring('${storageAccount}${resourceGroupIdUniqueified}',0,20)
//var keyVaultNameUniqueified = substring('${keyVaultName}${resourceGroupIdUniqueified}',0,20)
//var appInsightsNameUniqueified = '${appInsightsName}${resourceGroupIdUniqueified}'
//var containerRegistryNameUniqueified = '${containerRegistryName}${resourceGroupIdUniqueified}'
//var amlWorkspaceNameUniqueified = '${amlWorkspaceName}${resourceGroupIdUniqueified}'

// storage
module stg './modules/storage.template.bicep' = {
  name: storageAccount
  params:{
    storageAccountName: storageAccount
    location: location
    kind: kind
    accessTier: accessTier
    accountType: sku
  }
}

// key vault
module kv './modules/keyvault.template.bicep' = {
  name: keyVaultName
  params: {
    keyVaultName: keyVaultName
    location: location
  }
}

// application insights
module appInsightsResource './modules/appinsights.template.bicep' = {
  name:appInsightsName
  params: {
    appInsightsName: appInsightsName
    location: location
  }
}

// container registry
 module containerRegistryResource './modules/containerregistry.template.bicep' = {
  name: containerRegistryName
  params: {
    containerRegistryName: containerRegistryName
    location: location
  }
 }

 // azure machine learning
 module mlworkspace './modules/mlworkspace.template.bicep' = {
  name: amlWorkspaceName
  params: {
    amlWorkspaceName: amlWorkspaceName
    storageAccount: stg.name
    keyVaultName: kv.name
    appInsightsName: appInsightsResource.name
    containerRegistryName: containerRegistryResource.name
    location: location
  }
}

// virtual network
 module vnet './modules/virtualnetwork.template.bicep' = if(requiresPrivateWorkspace) {
  name: virtualNetworkName
  params: {
    location: location
    virtualNetworkName: virtualNetworkName
  }
}

// private endpoint
module privateEndpoint './modules/privateendpoint.template.bicep' = if(requiresPrivateWorkspace) {
  name: privateEndpointName
  params: {
    location: location
    privateEndpointName: privateEndpointName
    virtualNetworkName: vnet.name
    amlWorkspaceName: mlworkspace.name
  }
}

// private dns zone
module privateDnsZone './modules/privatednszone.template.bicep' = if(requiresPrivateWorkspace) {
  name: privateDnsZoneName
  params: {
    privateDnsZoneName: privateDnsZoneName
    virtualNetworkName: vnet.name
  }
  dependsOn: [
    privateEndpoint
  ]
}

// private dns zone link
module privateDnsZoneLink './modules/privatednsvnetlink.template.bicep' = if(requiresPrivateWorkspace) {
  name: privateDnsZoneLinkName
  params: {
    virtualNetworkName: vnet.name
    privateDnsZoneName: privateDnsZone.name
  }
}

// private dns zone group
module privateDnsZoneGroup './modules/privatednszonegroup.template.bicep' = if(requiresPrivateWorkspace) {
  name: privateDnsZoneGroupName
  params: {
    privateDnsZoneName: privateDnsZone.name
    privateDnsZoneGroupName: privateDnsZoneGroupName
    privateEndpointName: privateEndpoint.name
  }
}