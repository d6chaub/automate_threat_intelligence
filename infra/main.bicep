// _________________ Parameter Declarations _________________
param resourceEnvironmentPrefix string
param defaultTags object

// Existing resource group
//#disable-next-line BCP081 // Suppress type warning resulting from API documentation.
//resource resourceGroup 'Microsoft.Resources/resourceGroups@2023-07-01' existing = {
//  name: resourceGroupName
//}

// _________________ Resources to Deploy _________________

module keyVault './modules/keyVault.bicep' = {
  name: 'keyVaultDeployment'
  params: {
    keyVaultName: '${resourceEnvironmentPrefix}kv'
    location: resourceGroup().location
    tenantId: subscription().tenantId
    tags: defaultTags
  }
}
