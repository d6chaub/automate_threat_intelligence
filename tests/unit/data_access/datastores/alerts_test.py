import json
import pytest
from data_access.datastores.alerts import MongoConfig, AlertsDAO
from mongomock import MongoClient

# ToDo: Add unit tests for the other methods in the AlertsDAO class.
#       e.g. .add_alert_if_not_exists etc


@pytest.fixture(scope='module')
def load_mock_data():
    """Load mock alert data from a JSON file."""
    with open('tests/unit/data_access/mock_data/feedly_mock_data.json', 'r', encoding='utf-8') as file:
        return json.load(file)

@pytest.fixture(scope="module")
def mongo_config():
    """Provides a MongoConfig object configured for testing."""
    return MongoConfig(host='localhost', port=27017, database='test_db', alerts_collection='alerts')

@pytest.fixture(scope="function") # Don't want the (mock) database to persist across methods, as each on modifies it. The default scope is function.
# ToDo: Maybe in the future add more data to the mock data file and then can use module scope.
def alerts_dao(mongo_config):
    """Provides an AlertsDAO object with a mongomock MongoClient, setup once per class."""
    client = MongoClient()  # Using mongomock to simulate MongoClient
    return AlertsDAO(config=mongo_config, client=client)

class TestAlertsDAO:
    def test_add_alert(self, alerts_dao, load_mock_data):
        """Tests adding an alert and retrieving its ID using pre-loaded mock data."""
        alert_data = load_mock_data[0]  # Assuming the JSON is an array of alert data dictionaries
        result_id = alerts_dao.add_alert(alert_data)
        assert result_id is not None
        stored_alert = alerts_dao.get_alert(result_id)
        assert stored_alert['title'] == alert_data['title']
    
    def test_add_alerts(self, alerts_dao, load_mock_data):
        """Tests adding multiple alerts and retrieving their IDs using pre-loaded mock data."""
        result_ids = alerts_dao.add_alerts(load_mock_data)
        assert len(result_ids) == len(load_mock_data)
        stored_alerts = alerts_dao.get_all_alerts()
        assert len(stored_alerts) == len(load_mock_data)
        assert set(alert['title'] for alert in stored_alerts) == set(item['title'] for item in load_mock_data)

    def test_delete_alert(self, alerts_dao, load_mock_data):
        """Tests deleting an alert using pre-loaded mock data."""
        alert_data = load_mock_data[1]  # Use another item from the mock data
        result_id = alerts_dao.add_alert(alert_data)
        delete_result = alerts_dao.delete_alert(result_id)
        assert delete_result.deleted_count == 1
        assert alerts_dao.get_alert(result_id) is None

    def test_get_alert(self, alerts_dao, load_mock_data):
        """Tests retrieving a single alert using pre-loaded mock data."""
        alert_data = load_mock_data[0]  # Use another item from the mock data
        result_id = alerts_dao.add_alert(alert_data)
        retrieved_alert = alerts_dao.get_alert(result_id)
        assert retrieved_alert['_id'] == result_id
        assert retrieved_alert['title'] == alert_data['title']

    def test_get_all_alerts(self, alerts_dao, load_mock_data):
        """Tests retrieving all alerts from the collection using pre-loaded mock data."""
        alerts_dao.collection.delete_many({})  # Clear the collection first
        for alert in load_mock_data:  # Assume load_mock_data contains multiple alert items
            alerts_dao.add_alert(alert)
        all_alerts = alerts_dao.get_all_alerts()
        assert len(all_alerts) == len(load_mock_data)
        assert set(alert['title'] for alert in all_alerts) == set(item['title'] for item in load_mock_data)
