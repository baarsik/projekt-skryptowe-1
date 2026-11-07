using './hosting.bicep'

param location = 'polandcentral'
param staticSiteLocation = 'westeurope'
param frontendName = 'projekt-skryptowe-1-web'
param backendName = 'projekt-skryptowe-1-api-baarsik'
param appServicePlanId = '/subscriptions/8117cfd0-f60d-4827-95de-824dcf3e9959/resourceGroups/GrandDuchyResourceGroup-PolandCentral/providers/Microsoft.Web/serverfarms/ASP-GrandDuchyResourceGroupPolandCe-9c45'
param githubOidcSubjectPrefix = 'repo:baarsik@10713566/projekt-skryptowe-1@1431996033'
param tags = {
  project: 'projekt-skryptowe-1'
  environment: 'dev'
  managedBy: 'Bicep'
}
