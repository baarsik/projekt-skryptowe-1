param location string
param sqlServerName string
param databaseName string
param tags object

resource server 'Microsoft.Sql/servers@2023-08-01' existing = {
  name: sqlServerName
}

resource database 'Microsoft.Sql/servers/databases@2023-08-01' = {
  parent: server
  name: databaseName
  location: location
  tags: tags
  sku: {
    name: 'GP_S_Gen5_2'
    tier: 'GeneralPurpose'
    family: 'Gen5'
    capacity: 2
  }
  properties: {
    autoPauseDelay: 60
    minCapacity: json('0.5')
    maxSizeBytes: 34359738368
    requestedBackupStorageRedundancy: 'Local'
    zoneRedundant: false
    useFreeLimit: true
    freeLimitExhaustionBehavior: 'AutoPause'
  }
}

output databaseResourceId string = database.id
