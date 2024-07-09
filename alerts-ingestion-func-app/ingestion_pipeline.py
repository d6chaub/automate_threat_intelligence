"""
Script should be called by the 'ingestion_pipeline_trigger.sh' script in the same dir.
"""
#import logging
#import os
#
#from azure.cosmos import CosmosClient
#from azure.identity import DefaultAzureCredential
#from pymongo import MongoClient
#
#from config_managers.configs_manager import ConfigsManager
#from data_accessors.datastores.alerts import (AlertsDAOCosmos, AlertsDAOMongo,
#                                              CosmosConfig, MongoConfig)
#from data_accessors.fetchers import FetcherFactory
#from data_accessors.fetchers.feedly import FeedlyConfig
#
#logging.basicConfig(level=logging.INFO)
#
#config_manager = ConfigsManager() # Loads configs from environment variables, keyvault secrets, and config files.
#
## Instantiate a dao for the Feedly data source.
#feedly_config: FeedlyConfig = config_manager.retrieve_config(FeedlyConfig)
#feedly_fetcher = FetcherFactory.create_connection(feedly_config)
#
## Create connection to the main data store.
#if os.getenv("IS_LOCAL") == "True": # CosmosDB local emulator won't run on Mac M1, so I use MongoDB for local development.
#    mongo_config: MongoConfig = config_manager.retrieve_config(MongoConfig)
#    mongo_client = MongoClient(mongo_config.host, mongo_config.port)
#    alerts_permanent_datastore = AlertsDAOMongo(mongo_config, mongo_client)
#else:
#    # For Azure deployments, use managed identity to authenticate with CosmosDB.
#    cosmos_config: CosmosConfig = config_manager.retrieve_config(CosmosConfig)
#    cosmos_client = CosmosClient(cosmos_config.url, credential=DefaultAzureCredential())
#    alerts_permanent_datastore = AlertsDAOCosmos(cosmos_config, cosmos_client)

def run_ingestion_pipeline():
    ################TEMP DEBUG (then put it back above)####################
    import logging
    logging.info("The run ingestion pipeline function has been triggered.")
    try:
        import os

        from azure.cosmos import CosmosClient
        from azure.identity import DefaultAzureCredential
        from pymongo import MongoClient

        from config_managers.configs_manager import ConfigsManager
        from data_accessors.datastores.alerts import (AlertsDAOCosmos, AlertsDAOMongo,
                                                      CosmosConfig, MongoConfig)
        from data_accessors.fetchers import FetcherFactory
        from data_accessors.fetchers.feedly import FeedlyConfig

        logging.debug("CHECKING THAT LOGGING.DEBUG WORKS IN THE FUNCTION.")

        # ToDo: At some point replace the ConfigsManager approach with dependency injection?
        config_manager = ConfigsManager() # Loads configs from environment variables, keyvault secrets, and config files.

        # Instantiate a dao for the Feedly data source.
        feedly_config: FeedlyConfig = config_manager.retrieve_config(FeedlyConfig)
        feedly_fetcher = FetcherFactory.create_connection(feedly_config)

        # Create connection to the main data store.
        if os.getenv("IS_LOCAL") == "True": # CosmosDB local emulator won't run on Mac M1, so I use MongoDB for local development.
            mongo_config: MongoConfig = config_manager.retrieve_config(MongoConfig)
            mongo_client = MongoClient(mongo_config.host, mongo_config.port)
            alerts_permanent_datastore = AlertsDAOMongo(mongo_config, mongo_client)
        else:
            # For Azure deployments, use managed identity to authenticate with CosmosDB.
            cosmos_config: CosmosConfig = config_manager.retrieve_config(CosmosConfig)
            cosmos_client = CosmosClient(cosmos_config.url, credential=DefaultAzureCredential())
            alerts_permanent_datastore = AlertsDAOCosmos(cosmos_config, cosmos_client)
            alerts_permanent_datastore.debug_list_all_dbs_and_cols()
    except Exception as e:
        logging.error('Error in the run_ingestion_pipeline function: %s', e)
        raise e
    #################################################


    logging.info("We got past the setup stage of the function.")
    # Fetch recent articles from Feedly.
    all_articles: dict = feedly_fetcher.fetch_alerts()

    # Save the articles to the main db.
    inserted_ids = alerts_permanent_datastore.add_alerts_if_not_exist(all_articles)
    if inserted_ids:
        logging.info("Inserted %s new alerts to the main database.", {len(inserted_ids)})
        alerts_already_present = len(all_articles) - len(inserted_ids)
        if alerts_already_present:
            logging.debug(
                "%s alerts not added to the main database, as already present.",
                {len(all_articles) - len(inserted_ids)}
            )
    else:
        logging.info("No new alerts detected since last refresh.")

    # Add new alerts to the processing queue.
    #### use 'inserted_ids' for this.