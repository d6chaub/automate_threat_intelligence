import json
import logging
from pymongo import MongoClient
from pydantic import BaseModel, ValidationError
from .alerts import AlertsDAO, MongoConfig

# Define the mapping of data source types to their configurations and DAOs
DATASTORE_MAP = {
    "MongoDB": {
        "config": MongoConfig,
        "DAO": AlertsDAO
    }
    # Add other data stores here
}

class DataStoreFactory:
    """
    Factory class to initialize datastore configurations using environment variables.
    
    Supported DAO types:
    - Alerts (MongoDB)
    """

    @staticmethod
    def load_configs(datastore: str):
        """
        Get the configuration for the specified data store using environment variables.

        Args:
            datastore (str): The type of data store, e.g. "MongoDB".

        Returns:
            BaseSettings: An instance of the configuration class with values loaded from the environment.

        Raises:
            ValueError: If the data source is unknown.
            ValidationError: If environment configuration validation fails.
        """
        if datastore not in DATASTORE_MAP:
            raise ValueError(f"Unknown data source: {datastore}")

        config_class = DATASTORE_MAP[datastore]["config"]

        try:
            config = config_class()  # Automatically loads environment variables
            logging.info("%s configuration loaded successfully.", datastore)
            logging.debug("%s configuration: %s", datastore, config.model_dump_json())
        except ValidationError as e:
            logging.error("Configuration validation error for %s: %s", datastore, e)
            raise

        return config

    # Currently this method isn't being used!
    @staticmethod
    def get_dao(config: BaseModel, client: MongoConfig): # Add more types for type-checking if more datastores are added.
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
