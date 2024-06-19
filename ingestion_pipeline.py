"""
Script should be called by the 'ingestion_pipeline_trigger.sh' script in the same dir.
"""
import logging
import os
from pymongo import MongoClient
from data_access.datastores import DataStoreFactory
from data_access.datastores.alerts import MongoConfig, AlertsDAO
from data_access.fetchers.feedly import FeedlyConfig
from data_access.fetchers import FetcherFactory

logging.basicConfig(level=logging.INFO)

config_dir = 'config'

# Initialize Feedly Data Access Object.
config: FeedlyConfig = FetcherFactory.load_configs(
    os.path.join(config_dir, 'local', 'feedly_config.json'),
    'Feedly'
)
feedly_fetcher = FetcherFactory.get_fetcher(config)

# Fetch recent articles from Feedly.
all_articles: dict = feedly_fetcher.fetch_alerts()

# Configure the MongoDB Data Access Object.
config: MongoConfig = DataStoreFactory.load_configs("MongoDB")
client = MongoClient(config.host, config.port)
alerts_datastore = AlertsDAO(config, client)

# Save the articles to the MongoDB Datastore in docker container.
inserted_ids = alerts_datastore.add_alerts_if_not_exist(all_articles)
if inserted_ids:
    logging.info("Inserted %s new alerts to the mongo database.", {len(inserted_ids)})

    alerts_already_present = len(all_articles) - len(inserted_ids)
    if alerts_already_present:
        logging.debug(
            "%s alerts not added to the mongo as already present in the database.",
            {len(all_articles) - len(inserted_ids)}
        )
else:
    logging.info("No new alerts to insert to the mongo database.")