param keyVaultName string
param location string
param tenantId string
param tags object

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenantId
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
    enableRbacAuthorization: true
    enablePurgeProtection: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
  }
  tags: tags
}

// Outputs.
output keyVaultName string = keyVault.name
