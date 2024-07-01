import pytest

from data_accessors.config import ConfigManager
from data_accessors.datastores.alerts import MongoConfig


class TestConfigManager: # mock_config_manager is a fixture from conftest.py
    def test_initialize_config_manager(self, mock_config_manager: ConfigManager):
        """Test the singleton pattern for the ConfigManager."""
        assert  isinstance(mock_config_manager, ConfigManager)

    def test_load_app_config_valid_name(self, mock_config_manager: ConfigManager): # mock_config_manager is a fixture from conftest.py
        """Test behavior with a valid datastore type."""
        valid_config_name = "MongoDB"
        config = mock_config_manager.retrieve_config(valid_config_name)
        assert isinstance(config, MongoConfig)
    
    
    def test_load_app_config_invalid_name(self, mock_config_manager: ConfigManager): # mock_config_manager is a fixture from conftest.py
        """Test behavior with an invalid datastore type."""
        invalid_config_name = "InvalidSource"
        expected_error_message = f"Configuration for data source '{invalid_config_name}' was not loaded into the ConfigManager singleton upon initialization."
        with pytest.raises(ValueError) as exc_info:
            mock_config_manager.retrieve_config(invalid_config_name)
        assert expected_error_message in str(exc_info.value)