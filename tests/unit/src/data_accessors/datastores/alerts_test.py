""" Note that this module depends on the fixtures from conftest.py, which are made available automatically by pytest. """
import json
from unittest.mock import Mock, patch

import pydantic_core._pydantic_core as _pydantic_core
import pytest
from mongomock import MongoClient
from pydantic_settings import BaseSettings

from config_managers.configs_manager import ConfigsManager
from data_accessors.datastores.alerts import AlertsDAOMongo, MongoConfig

# ToDo: Add unit tests for the other methods in the AlertsDAO class.
#       e.g. .add_alert_if_not_exists etc


@pytest.fixture(scope="function")
def fake_mongo_config(fake_config_manager: ConfigsManager): # fake_config_manager is a fixture from conftest.py
    """Provides a MongoConfig object configured for testing."""
    return fake_config_manager.retrieve_config(MongoConfig)


@pytest.fixture(scope="function")
def fake_mongo_client(fake_mongo_config: MongoConfig):
    """Provides a mock MongoClient object for testing."""
    return MongoClient(fake_mongo_config.host, fake_mongo_config.port)  # Using mongomock to simulate MongoClient

@pytest.fixture(scope="function") # Don't want the (mock) database to persist across methods, as each on modifies it. The default scope is function.
# ToDo: Maybe in the future add more data to the mock data file and then can use module scope.
def fake_alerts_dao(fake_mongo_config, fake_mongo_client):
    """Provides an AlertsDAO object with a mongomock MongoClient, setup once per class."""
    return AlertsDAOMongo(config=fake_mongo_config, client=fake_mongo_client)


class TestMongoConfig:
    def test_mongo_config_initialization_valid_params(self, fake_mongo_config):
        """Test loading valid configuration using environment variables."""
        assert isinstance(fake_mongo_config, MongoConfig)
        assert fake_mongo_config.host == "localhost"
        assert fake_mongo_config.port == 27017
        assert fake_mongo_config.alerts_database_id == "threat_intelligence"
        assert fake_mongo_config.alerts_collection_id == "alerts"
    def test_mongo_config_initialization_invalid_port(self, load_env_vars, monkeypatch): # load_env_vars is a fixture from conftest.py
        """
        Test loading invalid configuration using environment variables.
        Note: Initializing the ConfigsManager depends on both envs vars (for MongoDB) and a config file (for alerts sources).
        This coupling is part of the intended design, to keep the interface of the ConfigsManager class simple.
        Here we are just testing a misconfig of the env vars - we assume the config file is correct (tested elsewhere).
        """
        ConfigsManager.reset() # Singleton reset before and after to avoid state leakage.
        monkeypatch.setenv("MONGO_PORT", "This string is not an integer.")
        expected_error_message = "Input should be a valid integer, unable to parse string as an integer"
        import os
        for k,v in os.environ.items():
            print(k,v)
        with pytest.raises(_pydantic_core.ValidationError) as exc_info:
            config_manager = ConfigsManager()
        assert expected_error_message in str(exc_info.value)
        ConfigsManager.reset()
    def test_mongo_config_initialization_invalid_string(self, load_env_vars, monkeypatch): # load_env_vars is a fixture from conftest.py
        """
        Test loading invalid configuration using environment variables.
        Note: Initializing the ConfigsManager depends on both envs vars (for MongoDB) and a config file (for alerts sources).
        This coupling is part of the intended design, to keep the interface of the ConfigsManager class simple.
        Here we are just testing a misconfig of the env vars - we assume the config file is correct (tested elsewhere).
        """
        ConfigsManager.reset() # Singleton reset before and after to avoid state leakage.
        monkeypatch.setenv("MONGO_HOST", "") # Setting a required string value to the empty string
        expected_error_message = "String should have at least 1 character"
        with pytest.raises(_pydantic_core.ValidationError) as exc_info:
            config_manager = ConfigsManager(
                'tests/unit/data_accessors/config/fake_alerts_sources.yaml'
            )
        assert expected_error_message in str(exc_info.value)
        ConfigsManager.reset()



class TestAlertsDAO:
    # fake_feedly_data is a fixture from conftest.py
    def test_initialize_mongo_dao_valid(self, fake_alerts_dao):
        """Test getting a DAO with valid configuration."""
        assert isinstance(fake_alerts_dao, AlertsDAOMongo)
    def test_add_alert_if_not_exists(self, fake_alerts_dao, fake_feedly_data):
        """Tests adding an alert only if it does not already exist in the collection."""
        alert_data = fake_feedly_data[0]
        # Add alert for the first time
        result_id = fake_alerts_dao.add_alert_if_not_exists(alert_data)
        assert result_id is not None
        # Try to add the same alert again
        result_id_duplicate = fake_alerts_dao.add_alert_if_not_exists(alert_data)
        assert result_id_duplicate is None

    def test_add_alerts_if_not_exist(self, fake_alerts_dao, fake_feedly_data):
        """Tests adding multiple alerts only if they do not already exist in the collection."""
        # Add multiple alerts for the first time
        result_ids = fake_alerts_dao.add_alerts_if_not_exist(fake_feedly_data)
        assert len(result_ids) == len(fake_feedly_data)
        # Attempt to add the same alerts again
        result_ids_duplicate = fake_alerts_dao.add_alerts_if_not_exist(fake_feedly_data)
        assert not result_ids_duplicate  # No new alerts should be added
    
    def test_delete_alert(self, fake_alerts_dao, fake_feedly_data):
        """Tests deleting an alert using pre-loaded mock data."""
        alert_data = fake_feedly_data[1]  # Use another item from the mock data
        result_id = fake_alerts_dao.add_alert_if_not_exists(alert_data)
        delete_result = fake_alerts_dao.delete_alert(result_id)
        assert delete_result.deleted_count == 1
        assert fake_alerts_dao.get_alert(result_id) is None

    def test_get_alert(self, fake_alerts_dao, fake_feedly_data):
        """Tests retrieving a single alert using pre-loaded mock data."""
        alert_data = fake_feedly_data[0]  # Use another item from the mock data
        result_id = fake_alerts_dao.add_alert_if_not_exists(alert_data)
        retrieved_alert = fake_alerts_dao.get_alert(result_id)
        assert retrieved_alert['_id'] == result_id
        assert retrieved_alert['title'] == alert_data['title']

    def test_get_all_alerts(self, fake_alerts_dao, fake_feedly_data):
        """Tests retrieving all alerts from the collection using pre-loaded mock data."""
        fake_alerts_dao.collection.delete_many({})  # Clear the collection first
        for alert in fake_feedly_data:  # Assume fake_feedly_data contains multiple alert items
            fake_alerts_dao.add_alert_if_not_exists(alert)
        all_alerts = fake_alerts_dao.get_all_alerts()
        assert len(all_alerts) == len(fake_feedly_data)
        assert set(alert['title'] for alert in all_alerts) == set(item['title'] for item in fake_feedly_data)