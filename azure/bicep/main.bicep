// Azure infrastructure-as-code for the DACH ESG, Climate Risk & CSRD Intelligence Platform.
// Deploys to a single EU region (default: germanywestcentral) to keep data in-jurisdiction.
// Deploy: az deployment group create -g <rg> -f main.bicep -p environmentName=dev

@description('Short environment name, e.g. dev, test, prod')
param environmentName string = 'dev'

@description('Azure region — kept in EU/DACH for data residency')
param location string = 'germanywestcentral'

var namePrefix = 'dachesg-${environmentName}'

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: toLower(replace('${namePrefix}sa', '-', ''))
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storage
  name: 'default'
}

resource rawContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'raw'
}
resource bronzeContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'bronze'
}
resource silverContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'silver'
}
resource goldContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'gold'
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${namePrefix}-kv'
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    accessPolicies: []
  }
}

resource sqlServer 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: '${namePrefix}-sql'
  location: location
  properties: {
    administratorLogin: 'esgadmin'
    administratorLoginPassword: 'ReplaceWithKeyVaultRef!' // pull from Key Vault in real pipelines, never inline
    minimalTlsVersion: '1.2'
  }
}

resource sqlDb 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  parent: sqlServer
  name: 'esg_platform'
  location: location
  sku: { name: 'Basic', tier: 'Basic' }
}

resource functionAppPlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${namePrefix}-plan'
  location: location
  sku: { name: 'Y1', tier: 'Dynamic' }
}

resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${namePrefix}-func'
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: functionAppPlan.id
    siteConfig: {
      appSettings: [
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'python' }
        { name: 'AzureWebJobsStorage', value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name}' }
      ]
    }
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${namePrefix}-log'
  location: location
  properties: { retentionInDays: 30 }
}

output storageAccountName string = storage.name
output keyVaultName string = keyVault.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output functionAppName string = functionApp.name
