@description('name for the private dns zone resource')
param privateDnsZoneName string

@description('Name of the virtual network resource.')
param virtualNetworkName string

resource vnet 'Microsoft.Network/virtualNetworks@2019-11-01' existing = {
    name: virtualNetworkName
  }

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
    name: privateDnsZoneName
    location: 'global'
    properties: {}
        dependsOn: [
        vnet
    ]    
  }