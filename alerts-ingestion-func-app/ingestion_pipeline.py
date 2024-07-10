"""
Script should be called by the 'ingestion_pipeline_trigger.sh' script in the same dir.
"""

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

        from models.alerts_table_document import AlertDocument

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
            alerts_db = AlertsDAOMongo(mongo_config, mongo_client)
        else:
            # For Azure deployments, use managed identity to authenticate with CosmosDB.
            cosmos_config: CosmosConfig = config_manager.retrieve_config(CosmosConfig)
            cosmos_client = CosmosClient(cosmos_config.url, credential=DefaultAzureCredential())
            alerts_db = AlertsDAOCosmos(cosmos_config, cosmos_client)
            alerts_db.debug_list_all_dbs_and_cols()
    except Exception as e:
        logging.error('Error in the run_ingestion_pipeline function: %s', e)
        raise e
    #################################################

    logging.info("We got past the setup stage of the function.")

    # Fetch recent articles from Feedly.
    alerts_all_streams: list[AlertDocument] = feedly_fetcher.fetch_alerts()

    # Save the alerts to db(s).
    new_alerts_counter: int = 0
    for alert in alerts_all_streams:
        # Add to main alerts db.
        inserted_id = alerts_db.add_alert_if_not_duplicate(alert)

        # If alert was added for first time, also add to triage staging db, for easy rendering for the frontend.
        if inserted_id:
            logging.info("Added alert with id: %s", inserted_id)
            # ToDo: HERE use the inserted id to add to the triage staging db.
            new_alerts_counter += 1
        else:
            logging.debug("Alert with publication_source_url %s already exists in the main database.", alert.publication_source_url) # Access the source dict object for debugging.
    
    if new_alerts_counter > 0:
        logging.info("Added %s new alerts to the main database.", new_alerts_counter)
        logging.info("%s alerts were already present in the main database (based on the publisher's source url) so were skipped.", len(alerts_all_streams) - new_alerts_counter)
    else:
        logging.info("No new alerts detected since last refresh.")
    # ToDo: Update the unit tests to reflect new structure.
    # Add new alerts to the processing queue.
    #### use 'inserted_ids' for this.