param location string
param staticSiteLocation string
param frontendName string
param backendName string
param appServicePlanId string
param tags object
// GitHub's immutable subject prefix includes owner and repository IDs.
param githubOidcSubjectPrefix string = 'repo:baarsik@10713566/projekt-skryptowe-1@1431996033'

resource frontend 'Microsoft.Web/staticSites@2024-11-01' = {
  name: frontendName
  location: staticSiteLocation
  tags: tags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    provider: 'Custom'
    stagingEnvironmentPolicy: 'Disabled'
    buildProperties: {
      skipGithubActionWorkflowGeneration: true
    }
  }
}

// Runtime identity remains separate from the GitHub deployment identity.
resource backend 'Microsoft.Web/sites@2024-11-01' = {
  name: backendName
  location: location
  kind: 'app,linux'
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlanId
    enabled: true
    httpsOnly: true
    clientAffinityEnabled: false
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.14'
      appCommandLine: 'python -m uvicorn main:app --host 0.0.0.0 --port 8000'
      alwaysOn: false
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      scmMinTlsVersion: '1.2'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
      ]
    }
  }
}

resource deploymentIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'id-projekt-skryptowe-1-deploy'
  location: location
  tags: tags
}

resource githubMain 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2024-11-30' = {
  parent: deploymentIdentity
  name: 'github-main'
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: '${githubOidcSubjectPrefix}:ref:refs/heads/main'
    audiences: [
      'api://AzureADTokenExchange'
    ]
  }
}

var websiteContributorRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'de139f84-1756-47ae-9be6-808fbbe84772')

resource backendDeploymentRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(backend.id, deploymentIdentity.id, websiteContributorRoleId)
  scope: backend
  properties: {
    roleDefinitionId: websiteContributorRoleId
    principalId: deploymentIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

output frontendHostname string = frontend.properties.defaultHostname
output frontendResourceId string = frontend.id
output backendResourceId string = backend.id
output backendPrincipalId string = backend.identity.principalId
output backendHostname string = backend.properties.defaultHostName
output deploymentClientId string = deploymentIdentity.properties.clientId
output deploymentTenantId string = deploymentIdentity.properties.tenantId
output deploymentSubscriptionId string = subscription().subscriptionId

// SQL data-plane permissions are granted separately inside rachunki-db by its admin.
resource migrationIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'id-projekt-skryptowe-1-migrate'
  location: location
  tags: tags
}

resource migrationGithubMain 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2024-11-30' = {
  parent: migrationIdentity
  name: 'github-main'
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: '${githubOidcSubjectPrefix}:ref:refs/heads/main'
    audiences: [
      'api://AzureADTokenExchange'
    ]
  }
}

output migrationClientId string = migrationIdentity.properties.clientId
output migrationPrincipalId string = migrationIdentity.properties.principalId
