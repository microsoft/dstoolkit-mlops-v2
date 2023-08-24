@description('The location into which your Azure resources should be deployed.')
param location string

@description('name for the app insights resource')
param appInsightsName string

resource name_resource 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}
