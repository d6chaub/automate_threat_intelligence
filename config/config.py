import logging
import os

import yaml

from data_access.datastores.alerts import MongoConfig
from data_access.fetchers.feedly import FeedlyConfig

DATA_FETCHERS_CONFIG_CLASS_MAP = {
    "Feedly": FeedlyConfig,
}

DATASTORES_CONFIG_CLASS_MAP = {
    "MongoDB": MongoConfig,
}

MONGODB_ENV_VARS = [
    "MONGO_HOST",
    "MONGO_PORT",
    "MONGO_DB",
    "MONGO_ALERTS_COLLECTION"
]

class ConfigManager:
    """
    Singleton class to manage configurations for different data sources.
    
    Configuration data is stored in a YAML file and also as environment variables.
    
    Configs from both sources are loaded upon initialisation and stored
    as a instance variable on the singleton object throughout the application
    lifecycle.

    """
    _instance = None

    # Work out how to set the config path
    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.configs = {}
            cls._instance._initialize_ingestion_sources_configs(config_path)
            cls._instance._initialize_datastore_configs()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Primary used for testing to avoid state leakage"""
        cls._instance = None
    
    # ToDo: Document how the value checking is done with pydantic. 
    def _initialize_ingestion_sources_configs(self, config_path) -> None:
        with open(config_path, 'r', encoding="utf-8") as file:
            source_config_dicts = yaml.safe_load(file)

        if "data_sources" not in source_config_dicts:
            raise ValueError("No source configurations for the ingestion pipeline found in the file.")
        
        source_config_dicts = source_config_dicts["data_sources"]

        # Check the ingestion sources present in the config file.
        # If a config is not found in the config file that should be there,
        # raise an error.
        for source_name, config_class in DATA_FETCHERS_CONFIG_CLASS_MAP.items():
            if source_name in source_config_dicts:
                source_config_dict = source_config_dicts[source_name]
            else:
                raise ValueError(
                    f"Configuration for data source '{source_name}' "
                    f"not found in the configuration file '{config_path}'."
                    f"Please check the configuration file and re-run the app."
                )
            self.configs[source_name] = config_class(**source_config_dict) # ToDo: Ensure there is error-checking when this is initialised. Document here if there is.

        # Check if there are any extra sources in the config file that are not in the DATA_FETCHERS_CONFIG_CLASS_MAP
        #ToDo: Test this
        extra_sources = set(source_config_dicts.keys()) - set(DATA_FETCHERS_CONFIG_CLASS_MAP.keys())
        if extra_sources:
            logging.warning(
                "Found extra data sources in the configuration file '%s': %s."
                "These sources have not been integrated in the app, and will be ignored.",
                config_path, extra_sources
            )


    # ToDo: Document how the value checking is done with environment variables using pydantic_settings
    def _initialize_datastore_configs(self):
        for datastore_name, config_class in DATASTORES_CONFIG_CLASS_MAP.items():
            self.configs[datastore_name] = config_class() # ToDo: Ensure there is error-checking and null-checking of the the env vars when this is initialised. Document here if there is.


    # Accessor methods
    def retrieve_config(self, data_source: str):
        """
        Returns the configuration object for a data access object.
        """
        if data_source in self.configs:
            return self.configs[data_source]
        # Update this error message to be better and more informative.
        raise ValueError(
            f"Configuration for data source '{data_source}' "
            "was not loaded into the ConfigManager singleton upon initialization. "
            "Please check the alerts_source.yaml file for the data ingestion pipeline configs, "
            "and the environment variables for the datastore configs, "
            "then re-run the pipeline app."
        )