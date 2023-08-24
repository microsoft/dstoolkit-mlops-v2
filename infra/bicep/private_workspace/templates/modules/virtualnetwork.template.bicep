@description('The location into which your Azure resources should be deployed.')
param location string

@description('name for the virtual network resource')
param virtualNetworkName string

@description('The name of the public subnet to create.')
param publicSubnetName string = 'public-subnet'

@description('The name of the private subnet to create.')
param privateSubnetName string = 'private-subnet'

resource virtualNetwork 'Microsoft.Network/virtualNetworks@2019-11-01' = {
  name: virtualNetworkName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: publicSubnetName
        properties: {
          addressPrefix: '10.0.0.0/24'
        }
      }
      {
        name: privateSubnetName
        properties: {
          addressPrefix: '10.0.1.0/24'
        }
      }
    ]
  }
}