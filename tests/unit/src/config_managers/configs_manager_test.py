import pytest

from config_managers.configs_manager import ConfigsManager
from data_accessors.datastores.alerts import MongoConfig, CosmosConfig

class invalid_config_type:
    pass


class TestConfigsManager: # fake_config_manager is a fixture from conftest.py
    def test_initialize_config_manager(self, fake_config_manager: ConfigsManager):
        """Test the singleton pattern for the ConfigsManager."""
        assert  isinstance(fake_config_manager, ConfigsManager)

    def test_load_app_config_valid_name(self, fake_config_manager: ConfigsManager): # fake_config_manager is a fixture from conftest.py
        """Test behavior with a valid datastore type."""
        mongo_config = fake_config_manager.retrieve_config(MongoConfig)
        assert isinstance(mongo_config, MongoConfig)
        cosmos_config = fake_config_manager.retrieve_config(CosmosConfig)
        assert isinstance(cosmos_config, CosmosConfig)

    def test_load_app_config_invalid_name(self, fake_config_manager: ConfigsManager): # fake_config_manager is a fixture from conftest.py
        """Test behavior with an invalid datastore type."""
        expected_error_message = f"Configuration of type {invalid_config_type} could not be found in the loaded configurations."
        with pytest.raises(ValueError) as exc_info:
            fake_config_manager.retrieve_config(invalid_config_type)
        assert expected_error_message in str(exc_info.value)