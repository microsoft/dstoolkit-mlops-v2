@description('name for the container registry')
param containerRegistryName string

@description('The location into which your Azure resources should be deployed.')
param location string

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: containerRegistryName
  location: location
  sku: {
    name: 'Basic'
    #disable-next-line BCP073
    tier: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
  #disable-next-line BCP187
  scale: null
  tags: {
  }
}
