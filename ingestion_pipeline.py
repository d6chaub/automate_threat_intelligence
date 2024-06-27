"""
Script should be called by the 'ingestion_pipeline_trigger.sh' script in the same dir.
"""
import logging
import os

from pymongo import MongoClient

from config.config import ConfigManager
from data_access.datastores.alerts import AlertsDAO, MongoConfig
from data_access.fetchers import FetcherFactory
from data_access.fetchers.feedly import FeedlyConfig

logging.basicConfig(level=logging.INFO)

# Instantiate a ConfigManager Singleton object to load the configurations.
config_manager = ConfigManager(
    os.path.join(
        os.path.dirname(__file__),
        "config",
        "alerts_sources.yaml"
    )
)

# Instantiate a dao for the Feedly data source.
feedly_config: FeedlyConfig = config_manager.retrieve_config("Feedly")
feedly_fetcher = FetcherFactory.create_connection(feedly_config)

# Get credentials for MongoDB and create connection to the main data store.
config: MongoConfig = config_manager.retrieve_config("MongoDB")
client = MongoClient(config.host, config.port)
alerts_permanent_datastore = AlertsDAO(config, client)

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