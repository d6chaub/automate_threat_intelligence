import logging

from pydantic import BaseModel

from .abstract import DataFetcher
from .feedly import FeedlyConfig, FeedlyDAO
# ToDo: Do better type-hinting for the data_source_config param etc.
# ToDo: Add better documentation explaining the purpose of this class,
# and how it can be used to initialize different fetcher clients in a
# polymorphic way.


class FetcherFactory:
    """
    Factory class to initialize fetcher clients.

    Using this factory, you can loop through a configuration list of different
    data sources and initialize the corresponding fetcher client, dynamically.
    
    Currently supported data sources:
    - Feedly
    """
    ## Class Variables and Methods ##
    # Define the mapping of data source types to their configurations and clients
    CLASS_MAP = {
        "Feedly": { "config_class": FeedlyConfig, "dao_class": FeedlyDAO },
        # Add other data sources here
    }

    allowed_config_types = [
        class_objects["config_class"] for class_objects in CLASS_MAP.values()
    ]

    @classmethod
    def create_connection(cls, config_instance: BaseModel) -> DataFetcher:
        """
        Initialize and return the fetcher DAO for the specified data source.

        Args:
            XXXX

        Returns:
            object: An instance of the fetcher dao for a particular data source.

        Raises:
            ValueError: If the configuration type is unknown.
        """
        for mapping_dict in cls.CLASS_MAP.values():
            if type(config_instance) is mapping_dict["config_class"]:
                dao_class = mapping_dict["dao_class"]
                dao_instance = dao_class(config_instance)
                return dao_instance
        raise ValueError(
            "Invalid config type. "
            "Expected one of the supported configurations: "
            f"{cls.allowed_config_types}"
        )