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

@description('Name of the aml workspace resource.')
param amlWorkspaceName string

@description('Name of the vnet resource.')
param virtualNetworkName string

@description('Name of the private dns zone resource.')
param privateDnsZoneName string

@description('Name of the private dns zone link resource.')
param privateDnsZoneLinkName string

@description('Name of the private dns zone group resource.')
param privateDnsZoneGroupName string

@description('Name of the private endpoint resource.')
param privateEndpointName string


var resourceGroupIdUniqueified = substring(uniqueString(resourceGroup().id),0,7)
var storageAccountNameUniqueified = '${storageAccount}${resourceGroupIdUniqueified}'
var keyVaultNameUniqueified = '${keyVaultName}${resourceGroupIdUniqueified}'
var appInsightsNameUniqueified = '${appInsightsName}${resourceGroupIdUniqueified}'
var containerRegistryNameUniqueified = '${containerRegistryName}${resourceGroupIdUniqueified}'
var amlWorkspaceNameUniqueified = '${amlWorkspaceName}${resourceGroupIdUniqueified}'
var virtualNetworkNameUniqueified = '${virtualNetworkName}${resourceGroupIdUniqueified}'
// var privateDnsZoneNameUniqueified = '${privateDnsZoneName}${resourceGroupIdUniqueified}'
// var privateDnsZoneLinkNameUniqueified = '${privateDnsZoneLinkName}${resourceGroupIdUniqueified}'
// var privateDnsZoneGroupNameUniqueified = '${privateDnsZoneGroupName}${resourceGroupIdUniqueified}'
var privateEndpointNameUniqueified = '${privateEndpointName}${resourceGroupIdUniqueified}'

// storage
module stg './modules/storage.template.bicep' = {
  name: storageAccountNameUniqueified
  params:{
    storageAccountName: storageAccountNameUniqueified

    location: location
    kind: kind
    accessTier: accessTier
    accountType: sku
  }
}

// key vault
module kv './modules/keyvault.template.bicep' = {
  name: keyVaultNameUniqueified
  params: {
    keyVaultName: keyVaultNameUniqueified
    location: location
  }
}

// application insights
module appInsightsResource './modules/appinsights.template.bicep' = {
  name:appInsightsNameUniqueified
  params: {
    appInsightsName: appInsightsNameUniqueified
    location: location
  }
}

// container registry
 module containerRegistryResource './modules/containerregistry.template.bicep' = {
  name: containerRegistryNameUniqueified
  params: {
    containerRegistryName: containerRegistryNameUniqueified
    location: location
  }
 }


 // virtual network
 module vnet './modules/virtualnetwork.template.bicep' = {
  name: virtualNetworkNameUniqueified
  params: {
    location: location
    virtualNetworkName: virtualNetworkNameUniqueified
  }
}

 // azure machine learning
 module mlworkspace './modules/mlworkspace.template.bicep' = {
  name: amlWorkspaceNameUniqueified
  params: {
    amlWorkspaceName: amlWorkspaceNameUniqueified
    storageAccount: stg.name
    keyVaultName: kv.name
    appInsightsName: appInsightsResource.name
    containerRegistryName: containerRegistryResource.name
    location: location
  }
}

// private endpoint
module privateEndpoint './modules/privateendpoint.template.bicep' = {
  name: privateEndpointNameUniqueified
  params: {
    location: location
    privateEndpointName: privateEndpointNameUniqueified
    virtualNetworkName: vnet.name
    amlWorkspaceName: mlworkspace.name
  }
}

// private dns zone
module privateDnsZone './modules/privatednszone.template.bicep' = {
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
module privateDnsZoneLink './modules/privatednsvnetlink.template.bicep' = {
  name: privateDnsZoneLinkName
  params: {
    location: location
    privateDnsLinkName: privateDnsZoneLinkName
    virtualNetworkName: vnet.name
    privateDnsZoneName: privateDnsZone.name
  }
}

// private dns zone group
module privateDnsZoneGroup './modules/privatednszonegroup.template.bicep' = {
  name: privateDnsZoneGroupName
  params: {
    privateDnsZoneName: privateDnsZone.name
    privateDnsZoneGroupName: privateDnsZoneGroupName
    privateEndpointName: privateEndpoint.name
  }
}