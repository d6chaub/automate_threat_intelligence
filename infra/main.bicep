//__     __         _       _     _        ____            _                 _   _
//\ \   / /_ _ _ __(_) __ _| |__ | | ___  |  _ \  ___  ___| | __ _ _ __ __ _| |_(_) ___  _ __  ___
// \ \ / / _` | '__| |/ _` | '_ \| |/ _ \ | | | |/ _ \/ __| |/ _` | '__/ _` | __| |/ _ \| '_ \/ __|
//  \ V / (_| | |  | | (_| | |_) | |  __/ | |_| |  __/ (__| | (_| | | | (_| | |_| | (_) | | | \__ \
//   \_/ \__,_|_|  |_|\__,_|_.__/|_|\___| |____/ \___|\___|_|\__,_|_|  \__,_|\__|_|\___/|_| |_|___/
//
// ToDo: Deploy with deployment stack
param subscriptionId string // Needed to compile .biceparam file even though not used here. Used in other script.
param resourceGroupName string // Needed to compile .biceparam file even though not used here. Used in other script.

// Cosmos DB
param cosmosDbAccountName string
param cosmosDbAlertsDatabaseId string
param cosmosDbAlertsContainerId string

// Ingestion Pipeline Function App
param ingestionFunctionAppName string


//__  __           _ _  __         ____
//|  \/  | ___   __| (_)/ _|_   _  |  _ \ ___  ___  ___  _   _ _ __ ___ ___  ___
//| |\/| |/ _ \ / _` | | |_| | | | | |_) / _ \/ __|/ _ \| | | | '__/ __/ _ \/ __|
//| |  | | (_) | (_| | |  _| |_| | |  _ <  __/\__ \ (_) | |_| | | | (_|  __/\__ \
//|_|  |_|\___/ \__,_|_|_|  \__, | |_| \_\___||___/\___/ \__,_|_|  \___\___||___/
//                          |___/


//Add environment variables for Ingestion Pipeline Function App

resource ingestionFunctionApp 'Microsoft.Web/sites@2019-04-01' existing = {
  name: ingestionFunctionAppName
}

resource appSettings 'Microsoft.Web/sites/config@2020-12-01' = {
  name: 'appsettings'
  parent: ingestionFunctionApp
  properties: {
    // Add or modify environment variables here
    COSMOS_DB_ENDPOINT: 'TESTTESTTEST'
    ADDITIONAL_VARIABLE: 'testtesttest'
  }
}


// Create 'alerts' database and container in Cosmos DB

resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' existing = {
  name: cosmosDbAccountName
}

resource alertsDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = {
  name: cosmosDbAlertsDatabaseId
  parent: cosmosDbAccount
  properties: {
    resource: {
      id: cosmosDbAlertsDatabaseId
    }
    options: {}
  }
}

resource alertsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  name: cosmosDbAlertsContainerId
  parent: alertsDatabase
  properties: {
    resource: {
      id: cosmosDbAlertsContainerId
      partitionKey: {
        paths: [
          '/alertUrl'
        ]
        kind: 'Hash'
      }
    }
    options: {}
  }
}

// Notes
// - To debug any deployment variables, use the 'output' keyword, and see the results in the Azure Portal.
