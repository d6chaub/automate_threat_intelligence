import json
import logging
from pydantic import BaseModel, ValidationError
from .feedly import FeedlyDAO, FeedlyConfig


import json
import logging
from pydantic import BaseModel, ValidationError
from .feedly import FeedlyDAO, FeedlyConfig

# Define the mapping of data source types to their configurations and clients
DATA_SOURCE_MAP = {
    "Feedly": {
        "config": FeedlyConfig,
        "client": FeedlyDAO,
    },
    # Add other data sources here
}

class FetcherFactory:
    """
    Factory class to load configuration and initialize fetcher clients.

    Using this factory, you can loop through a configuration list of different
    data sources and initialize the corresponding fetcher client, dynamically.
    
    Supported data sources:
    - Feedly
    """

    @staticmethod
    def load_config(config_path: str, data_source: str):
        """
        Load the configuration for the specified data source from the given path.

        Args:
            config_path (str): The path to the configuration file.
            data_source (str): The type of data source.

        Returns:
            BaseModel: An instance of the configuration class.

        Raises:
            ValueError: If the data source is unknown or configuration validation fails.
        """
        if data_source not in DATA_SOURCE_MAP:
            raise ValueError(f"Unknown data source: {data_source}")

        with open(config_path, 'r') as file:
            config_data = json.load(file)
        
        config_class = DATA_SOURCE_MAP[data_source]["config"]

        try:
            config = config_class(**config_data)
            logging.info("%s configuration loaded successfully.", data_source)
            logging.debug("%s configuration: %s", data_source, config.model_dump_json())
        except ValidationError as e:
            logging.error("Configuration validation error for %s: %s", data_source, e)
            raise
        
        return config

    @staticmethod
    def get_fetcher(config: BaseModel):
        """
        Initialize and return the fetcher client based on the provided configuration.

        Args:
            config (BaseModel): The configuration instance.

        Returns:
            object: An instance of the fetcher client.

        Raises:
            ValueError: If the configuration type is unknown.
        """
        for data_source, mapping in DATA_SOURCE_MAP.items():
            if isinstance(config, mapping["config"]):
                client = mapping["client"](config)
                logging.info("%sDAO initialized successfully.", data_source)
                return client

        raise ValueError("Invalid config type. Expected one of the supported configurations.")
