param createMode string = 'default'

@description('name for the key vault')
param keyVaultName string

@description('The location into which your Azure resources should be deployed.')
param location string

resource name_resource 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    createMode: createMode
    enabledForTemplateDeployment: true
    accessPolicies: []
  }
  scale: null
  tags: {
  }
}
