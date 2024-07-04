using 'main.bicep'

// Shared configs

@description('The id of the subscription.')
param subscriptionId = 'a3c531dd-409f-4d4a-b076-0e2020958b66'

@description('The name of the resource group.')
param resourceGroupName = 'CRO-SOAR2-NonCRO-Dev'

// Cosmos DB

@description('The name of the Cosmos DB account.')
param cosmosDbAccountName = 'cro-soar2-noncro-dev'

@description('The ID of the Cosmos DB database.')
param cosmosDbAlertsDatabaseId = 'threat_intelligence'

@description('The ID of the Cosmos DB container.')
param cosmosDbAlertsContainerId  = 'alerts'

// Ingestion Pipeline Function App

@description('The name of the ingestion pipeline Function App.')
param ingestionFunctionAppName = 'Enrichment-D-DevOps-AutomateThreatIntel'
