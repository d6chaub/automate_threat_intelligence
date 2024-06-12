import json
import logging
from pymongo import MongoClient
from pydantic import BaseModel, ValidationError
from .alerts import AlertsDAO, MongoConfig

# Define the mapping of data source types to their configurations and DAOs
DATASTORE_MAP = {
    "MongoDB": {
        "config": MongoConfig,
    }
    # Add other data stores here
}

class DataStoreFactory:
    """
    Factory class to load configuration and initialize datastore DAOs.

    Using this factory, you can loop through a configuration list of different
    data stores and initialize the corresponding DAOs dynamically.
    
    Supported DAO types:
    - Alerts (MongoDB)
    """

    @staticmethod
    def load_config(config_path: str, datastore: str):
        """
        Load the configuration for the specified data store from the given path.

        Args:
            config_path (str): The path to the configuration file.
            datastore(str): The type of data store, e.g. "MongoDB".

        Returns:
            BaseModel: An instance of the configuration class.

        Raises:
            ValueError: If the data source is unknown or configuration validation fails.
        """
        if datastore not in DATASTORE_MAP:
            raise ValueError(f"Unknown data source: {datastore}")

        with open(config_path, 'r') as file:
            config_data = json.load(file)
        
        config_class = DATASTORE_MAP[datastore]["config"]

        try:
            config = config_class(**config_data)
            logging.info("%s configuration loaded successfully.", datastore)
            logging.debug("%s configuration: %s", datastore, config.model_dump_json())
        except ValidationError as e:
            logging.error("Configuration validation error for %s: %s", datastore, e)
            raise
        
        return config

    @staticmethod
    def get_dao(config: BaseModel, client: MongoClient):
        """
        Initialize and return the DAO based on the provided configuration.

        Args:
            config (BaseModel): The configuration instance.

        Returns:
            object: An instance of the DAO class.

        Raises:
            ValueError: If the configuration type is unknown.
        """
        for datastore, mapping in DATASTORE_MAP.items():
            if isinstance(config, mapping["config"]):
                dao = mapping["DAO"](config, client)
                logging.info("%sDAO initialized successfully.", datastore)
                return dao

        raise ValueError("Invalid config type. Expected one of the supported configurations.")
