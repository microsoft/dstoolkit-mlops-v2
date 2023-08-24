@description('The location into which your Azure resources should be deployed.')
param location string

@description('name for the private endpoint resource')
param privateEndpointName string

@description('name for the virtual network resource')
param virtualNetworkName string

@description('name for the azure machine learning resource')
param amlWorkspaceName string

resource vnet 'Microsoft.Network/virtualNetworks@2019-11-01' existing = {
    name: virtualNetworkName
  }

resource workspace 'Microsoft.MachineLearningServices/workspaces@2023-04-01' existing = {
name: amlWorkspaceName
}

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2021-08-01' = {
    name: privateEndpointName
    location: location
    properties: {
      subnet: {
        id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnet.name, vnet.properties.subnets[1].name)
      }
      privateLinkServiceConnections: [
        {
          name: privateEndpointName
          properties: {
            privateLinkServiceId: workspace.id
            groupIds: [
              'amlworkspace']
          }
        }
      ]
    }
  }