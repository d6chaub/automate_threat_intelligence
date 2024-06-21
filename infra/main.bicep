// _________________ Variable Declarations (from .parameters.json) _________________
param resourceEnvironmentPrefix string
param defaultTags object

// _________________ Secret Declarations (from keyvault) _________________

// Reference the keyvault module created below.
// Bicep resolves dependencies implicit dependencies and knows to handle the keyvault module deployment first.
resource kv 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: keyVault.outputs.keyVaultName
}
// Pass a secret to a module as a param. The module must have the corresponding
//      parameter with a secure() decorator.
//      e.g.
//            kv.getSecret('mySecret')



// _________________ Resources in RG _________________

module keyVault './modules/keyVault.bicep' = {
  name: 'keyVaultDeployment'
  params: {
    keyVaultName: '${resourceEnvironmentPrefix}kv'
    location: resourceGroup().location
    tenantId: subscription().tenantId
    tags: defaultTags
  }
}

// To debug any deployment variables, use the 'output' keyword, and see the results in the Azure Portal.
