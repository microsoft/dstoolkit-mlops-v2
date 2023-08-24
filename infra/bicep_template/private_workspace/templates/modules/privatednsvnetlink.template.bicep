@description('The location into which your Azure resources should be deployed.')
param location string

@description('name for the private dns link resource')
param privateDnsLinkName string

@description('name for the virtual network resource')
param virtualNetworkName string

@description('name for the private dns zone resource')
param privateDnsZoneName string

resource vnet 'Microsoft.Network/virtualNetworks@2019-11-01' existing = {
    name: virtualNetworkName
  }

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' existing = {
name: privateDnsZoneName
}

resource privateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
    parent: privateDnsZone
    name: '${privateDnsZoneName}-link' 
    location: 'global'
    properties: {
      registrationEnabled: false
      virtualNetwork: {
        id: vnet.id
      }
    }
  }