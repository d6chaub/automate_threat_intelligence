import json
import pytest
from mongomock import MongoClient
from unittest.mock import Mock, patch
from pydantic_settings import BaseSettings

from data_access.datastores.alerts import MongoConfig, AlertsDAO
from data_access.datastores import DataStoreFactory, MongoConfig


# ToDo: Add unit tests for the other methods in the AlertsDAO class.
#       e.g. .add_alert_if_not_exists etc


@pytest.fixture(scope='module')
def load_mock_data():
    """Load mock alert data from a JSON file."""
    with open('tests/unit/data_access/mock_data/feedly_mock_data.json', 'r', encoding='utf-8') as file:
        return json.load(file)

@pytest.fixture(scope="function")
def mock_mongo_config(monkeypatch):
    """Provides a MongoConfig object configured for testing."""
    monkeypatch.setenv("MONGO_HOST", "localhost")
    monkeypatch.setenv("MONGO_PORT", "27017")
    monkeypatch.setenv("MONGO_DATABASE", "threat_intelligence")
    monkeypatch.setenv("MONGO_ALERTS_COLLECTION", "alerts")
    config = DataStoreFactory.load_configs("MongoDB")
    return config
    
@pytest.fixture(scope="function")
def mock_mongo_client(mock_mongo_config):
    """Provides a mock MongoClient object for testing."""
    return MongoClient(mock_mongo_config.host, mock_mongo_config.port)  # Using mongomock to simulate MongoClient

@pytest.fixture(scope="function") # Don't want the (mock) database to persist across methods, as each on modifies it. The default scope is function.
# ToDo: Maybe in the future add more data to the mock data file and then can use module scope.
def alerts_dao(mock_mongo_config, mock_mongo_client):
    """Provides an AlertsDAO object with a mongomock MongoClient, setup once per class."""
    return AlertsDAO(config=mock_mongo_config, client=mock_mongo_client)


class TestDataStoreFactory:
    def test_load_mongo_config_valid(self, mock_mongo_config):
        """Test loading valid configuration using environment variables."""
        assert mock_mongo_config.host == "localhost"
        assert mock_mongo_config.port == 27017
        assert mock_mongo_config.database == "threat_intelligence"
        assert mock_mongo_config.alerts_collection == "alerts"

    def test_load_configs_invalid(self):
        """Test behavior with an invalid datastore type."""
        with pytest.raises(ValueError) as exc_info:
            DataStoreFactory.load_configs("InvalidDB")
        assert "Unknown data source: InvalidDB" in str(exc_info.value)

    # Currently the get_dao method is not being used, but it's good to have a test for it in case it's needed in the future.
    def test_get_mongo_dao_valid(self, mock_mongo_client, mock_mongo_config):
        """Test getting a DAO with valid configuration."""
        dao = DataStoreFactory.get_dao(mock_mongo_config, mock_mongo_client)
        assert dao is not None, "Mongo DAO was not succesfully initialised!"

    # Currently the get_dao method is not being used, but it's good to have a test for it in case it's needed in the future.
    def test_get_dao_invalid_config_type(self, mock_mongo_client, mock_mongo_config):
        """Test getting a DAO with an invalid configuration type."""
        with pytest.raises(ValueError) as exc_info:
            dao = DataStoreFactory.get_dao(BaseSettings(), mock_mongo_client)
        assert "Invalid config type. Expected one of the supported configurations." in str(exc_info.value)

class TestAlertsDAO:
    def test_add_alert_if_not_exists(self, alerts_dao, load_mock_data):
        """Tests adding an alert only if it does not already exist in the collection."""
        alert_data = load_mock_data[0]
        # Add alert for the first time
        result_id = alerts_dao.add_alert_if_not_exists(alert_data)
        assert result_id is not None
        # Try to add the same alert again
        result_id_duplicate = alerts_dao.add_alert_if_not_exists(alert_data)
        assert result_id_duplicate is None

    def test_add_alerts_if_not_exist(self, alerts_dao, load_mock_data):
        """Tests adding multiple alerts only if they do not already exist in the collection."""
        # Add multiple alerts for the first time
        result_ids = alerts_dao.add_alerts_if_not_exist(load_mock_data)
        assert len(result_ids) == len(load_mock_data)
        # Attempt to add the same alerts again
        result_ids_duplicate = alerts_dao.add_alerts_if_not_exist(load_mock_data)
        assert not result_ids_duplicate  # No new alerts should be added
    
    def test_delete_alert(self, alerts_dao, load_mock_data):
        """Tests deleting an alert using pre-loaded mock data."""
        alert_data = load_mock_data[1]  # Use another item from the mock data
        result_id = alerts_dao.add_alert_if_not_exists(alert_data)
        delete_result = alerts_dao.delete_alert(result_id)
        assert delete_result.deleted_count == 1
        assert alerts_dao.get_alert(result_id) is None

    def test_get_alert(self, alerts_dao, load_mock_data):
        """Tests retrieving a single alert using pre-loaded mock data."""
        alert_data = load_mock_data[0]  # Use another item from the mock data
        result_id = alerts_dao.add_alert_if_not_exists(alert_data)
        retrieved_alert = alerts_dao.get_alert(result_id)
        assert retrieved_alert['_id'] == result_id
        assert retrieved_alert['title'] == alert_data['title']

    def test_get_all_alerts(self, alerts_dao, load_mock_data):
        """Tests retrieving all alerts from the collection using pre-loaded mock data."""
        alerts_dao.collection.delete_many({})  # Clear the collection first
        for alert in load_mock_data:  # Assume load_mock_data contains multiple alert items
            alerts_dao.add_alert_if_not_exists(alert)
        all_alerts = alerts_dao.get_all_alerts()
        assert len(all_alerts) == len(load_mock_data)
        assert set(alert['title'] for alert in all_alerts) == set(item['title'] for item in load_mock_data)