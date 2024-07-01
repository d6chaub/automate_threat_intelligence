import logging
import os

import yaml
from data_accessors.datastores.alerts import MongoConfig
from data_accessors.fetchers.feedly import FeedlyConfig
from pydantic_settings import BaseSettings

CONFIGS = [
    FeedlyConfig,
    MongoConfig
]

class ConfigManager:
    """
    Singleton class to manage configurations for different data sources.
    
    Configuration data is stored as environment variables.
    
    Configs from both sources are loaded upon initialisation and stored
    as a instance variable on the singleton object throughout the application
    lifecycle.

    """
    _instance = None

    # Work out how to set the config path
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.configs = []
            cls._instance._initialize_configs()
        return cls._instance
    
    @classmethod
    def reload_configs(cls):
        """Primary used for testing to avoid state leakage"""
        cls._instance = None
        # ToDo: Here reload the configs by calling __new__ again or smt?
        # ToDo: Change the tests to use this as well

    # ToDo: Document how the value checking is done with environment variables using pydantic_settings
    def _initialize_configs(self):
        for config_class in CONFIGS:
            self.configs.append(config_class()) # The config classes are initialized with env vars, using pydantic_settings internally for validation and null-checks.

    # Accessor methods
    def retrieve_config(self, config_class: BaseSettings):
        """
        Returns the configuration settings for a data access object.

        Args:
            config_class:
                The class of the configuration object to retrieve.

        Returns:        
            The populated configuration instance of the config_class,
            using the values that were initialised at application startup.
        """
        for config_instance in self.configs:
            if isinstance(config_instance, config_class):
                return config_instance
        # Update this error message to be better and more informative.
        raise ValueError(
            f"Configuration of type {config_class} "
            "could not be found in the loaded configurations. "
            "Please ensure all environment variables are set correctly, "
            "then re-run the pipeline app."
        )