targetScope = 'subscription'

param resourceGroupName string = 'rg-projekt-skryptowe-1-dev'
param location string = 'polandcentral'
param staticSiteLocation string = 'westeurope'
param frontendName string = 'projekt-skryptowe-1-web'
param backendName string = 'projekt-skryptowe-1-api-baarsik'
param databaseName string = 'rachunki-db'
param sqlServerName string = 'grandduchy-server'
param sharedResourceGroupName string = 'GrandDuchyResourceGroup-PolandCentral'
param sharedAppServicePlanName string = 'ASP-GrandDuchyResourceGroupPolandCe-9c45'

var tags = {
  project: 'projekt-skryptowe-1'
  environment: 'dev'
  managedBy: 'Bicep'
}

resource projectGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

resource sharedGroup 'Microsoft.Resources/resourceGroups@2024-03-01' existing = {
  name: sharedResourceGroupName
}

module hosting './hosting.bicep' = {
  name: 'projekt-skryptowe-1-hosting'
  scope: projectGroup
  params: {
    location: location
    staticSiteLocation: staticSiteLocation
    frontendName: frontendName
    backendName: backendName
    appServicePlanId: resourceId(subscription().subscriptionId, sharedResourceGroupName, 'Microsoft.Web/serverfarms', sharedAppServicePlanName)
    tags: tags
  }
}

module database './database.bicep' = {
  name: 'projekt-skryptowe-1-database'
  scope: sharedGroup
  params: {
    location: location
    sqlServerName: sqlServerName
    databaseName: databaseName
    tags: tags
  }
}

output frontendHostname string = hosting.outputs.frontendHostname
output frontendResourceId string = hosting.outputs.frontendResourceId
output backendResourceId string = hosting.outputs.backendResourceId
output backendPrincipalId string = hosting.outputs.backendPrincipalId
output backendHostname string = hosting.outputs.backendHostname
output deploymentClientId string = hosting.outputs.deploymentClientId
output deploymentTenantId string = hosting.outputs.deploymentTenantId
output deploymentSubscriptionId string = hosting.outputs.deploymentSubscriptionId
output databaseResourceId string = database.outputs.databaseResourceId
output migrationClientId string = hosting.outputs.migrationClientId
output migrationPrincipalId string = hosting.outputs.migrationPrincipalId
