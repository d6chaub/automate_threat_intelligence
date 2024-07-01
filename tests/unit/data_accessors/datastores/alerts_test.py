""" Note that this module depends on the fixtures from conftest.py, which are made available automatically by pytest. """
import json
from unittest.mock import Mock, patch

import pydantic_core._pydantic_core as _pydantic_core
import pytest
from mongomock import MongoClient
from pydantic_settings import BaseSettings

from data_accessors.config import ConfigManager
from data_accessors.datastores.alerts import AlertsDAO, MongoConfig

# ToDo: Add unit tests for the other methods in the AlertsDAO class.
#       e.g. .add_alert_if_not_exists etc


@pytest.fixture(scope="function")
def mock_mongo_config(mock_config_manager: ConfigManager): # mock_config_manager is a fixture from conftest.py
    """Provides a MongoConfig object configured for testing."""
    config = mock_config_manager.retrieve_config("MongoDB")
    print("HELEFE;FLIJAERFO;IAERJF")
    print(type(config))
    return config
    
@pytest.fixture(scope="function")
def mock_mongo_client(mock_mongo_config: MongoConfig):
    """Provides a mock MongoClient object for testing."""
    return MongoClient(mock_mongo_config.host, mock_mongo_config.port)  # Using mongomock to simulate MongoClient

@pytest.fixture(scope="function") # Don't want the (mock) database to persist across methods, as each on modifies it. The default scope is function.
# ToDo: Maybe in the future add more data to the mock data file and then can use module scope.
def mock_alerts_dao(mock_mongo_config, mock_mongo_client):
    """Provides an AlertsDAO object with a mongomock MongoClient, setup once per class."""
    return AlertsDAO(config=mock_mongo_config, client=mock_mongo_client)


class TestMongoConfig:
    def test_mongo_config_initialization_valid_params(self, mock_mongo_config):
        """Test loading valid configuration using environment variables."""
        assert isinstance(mock_mongo_config, MongoConfig)
        assert mock_mongo_config.host == "localhost"
        assert mock_mongo_config.port == 27017
        assert mock_mongo_config.database == "threat_intelligence"
        assert mock_mongo_config.alerts_collection == "alerts"
    def test_mongo_config_initialization_invalid_port(self, monkeypatch):
        """
        Test loading invalid configuration using environment variables.
        Note: Initializing the ConfigManager depends on both envs vars (for MongoDB) and a config file (for alerts sources).
        This coupling is part of the intended design, to keep the interface of the ConfigManager class simple.
        Here we are just testing a misconfig of the env vars - we assume the config file is correct (tested elsewhere).
        """
        ConfigManager.reset() # Singleton reset before and after to avoid state leakage.
        monkeypatch.setenv("MONGO_PORT", "This string is not an integer.")
        expected_error_message = "Input should be a valid integer, unable to parse string as an integer"
        with pytest.raises(_pydantic_core.ValidationError) as exc_info:
            config_manager = ConfigManager(
                'tests/unit/data_accessors/config/mock_alerts_sources.yaml'
            )
        assert expected_error_message in str(exc_info.value)
        ConfigManager.reset()
    def test_mongo_config_initialization_invalid_string(self, monkeypatch):
        """
        Test loading invalid configuration using environment variables.
        Note: Initializing the ConfigManager depends on both envs vars (for MongoDB) and a config file (for alerts sources).
        This coupling is part of the intended design, to keep the interface of the ConfigManager class simple.
        Here we are just testing a misconfig of the env vars - we assume the config file is correct (tested elsewhere).
        """
        ConfigManager.reset() # Singleton reset before and after to avoid state leakage.
        monkeypatch.setenv("MONGO_HOST", "") # Setting a required string value to the empty string
        expected_error_message = "String should have at least 1 character"
        with pytest.raises(_pydantic_core.ValidationError) as exc_info:
            config_manager = ConfigManager(
                'tests/unit/data_accessors/config/mock_alerts_sources.yaml'
            )
        assert expected_error_message in str(exc_info.value)
        ConfigManager.reset()



class TestAlertsDAO:
    # mock_feedly_data is a fixture from conftest.py
    def test_initialize_mongo_dao_valid(self, mock_alerts_dao):
        """Test getting a DAO with valid configuration."""
        assert isinstance(mock_alerts_dao, AlertsDAO)
    def test_add_alert_if_not_exists(self, mock_alerts_dao, mock_feedly_data):
        """Tests adding an alert only if it does not already exist in the collection."""
        alert_data = mock_feedly_data[0]
        # Add alert for the first time
        result_id = mock_alerts_dao.add_alert_if_not_exists(alert_data)
        assert result_id is not None
        # Try to add the same alert again
        result_id_duplicate = mock_alerts_dao.add_alert_if_not_exists(alert_data)
        assert result_id_duplicate is None

    def test_add_alerts_if_not_exist(self, mock_alerts_dao, mock_feedly_data):
        """Tests adding multiple alerts only if they do not already exist in the collection."""
        # Add multiple alerts for the first time
        result_ids = mock_alerts_dao.add_alerts_if_not_exist(mock_feedly_data)
        assert len(result_ids) == len(mock_feedly_data)
        # Attempt to add the same alerts again
        result_ids_duplicate = mock_alerts_dao.add_alerts_if_not_exist(mock_feedly_data)
        assert not result_ids_duplicate  # No new alerts should be added
    
    def test_delete_alert(self, mock_alerts_dao, mock_feedly_data):
        """Tests deleting an alert using pre-loaded mock data."""
        alert_data = mock_feedly_data[1]  # Use another item from the mock data
        result_id = mock_alerts_dao.add_alert_if_not_exists(alert_data)
        delete_result = mock_alerts_dao.delete_alert(result_id)
        assert delete_result.deleted_count == 1
        assert mock_alerts_dao.get_alert(result_id) is None

    def test_get_alert(self, mock_alerts_dao, mock_feedly_data):
        """Tests retrieving a single alert using pre-loaded mock data."""
        alert_data = mock_feedly_data[0]  # Use another item from the mock data
        result_id = mock_alerts_dao.add_alert_if_not_exists(alert_data)
        retrieved_alert = mock_alerts_dao.get_alert(result_id)
        assert retrieved_alert['_id'] == result_id
        assert retrieved_alert['title'] == alert_data['title']

    def test_get_all_alerts(self, mock_alerts_dao, mock_feedly_data):
        """Tests retrieving all alerts from the collection using pre-loaded mock data."""
        mock_alerts_dao.collection.delete_many({})  # Clear the collection first
        for alert in mock_feedly_data:  # Assume mock_feedly_data contains multiple alert items
            mock_alerts_dao.add_alert_if_not_exists(alert)
        all_alerts = mock_alerts_dao.get_all_alerts()
        assert len(all_alerts) == len(mock_feedly_data)
        assert set(alert['title'] for alert in all_alerts) == set(item['title'] for item in mock_feedly_data)