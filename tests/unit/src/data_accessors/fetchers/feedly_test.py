import pydantic_core._pydantic_core as _pydantic_core
import pytest
from pydantic import BaseModel

from config_managers.configs_manager import ConfigsManager
from data_accessors.fetchers import FetcherFactory
from data_accessors.fetchers.feedly import FeedlyConfig, FeedlyDAO


class UnsupportedConfig(BaseModel):
    """A mock configuration class that is not supported by FetcherFactory."""
    pass

@pytest.fixture(scope="function")
def mock_feedly_config(mock_config_manager: ConfigsManager): # mock_config_manager is a fixture from conftest.py
    """Provides a FeedlyConfig object configured for testing."""
    feedly_config = mock_config_manager.retrieve_config("Feedly")
    return feedly_config

@pytest.fixture(scope="function")
def mock_feedly_dao(mock_feedly_config):
    """Provides a FeedlyClient object for testing."""
    return FetcherFactory.create_connection(mock_feedly_config)


class TestFeedlyConfig:
    def test_feedly_config_initialization_valid_params(self, mock_feedly_config):
        """Test loading valid configuration the yaml file."""
        assert isinstance(mock_feedly_config, FeedlyConfig)
        assert mock_feedly_config.access_token == "abababab"
        assert mock_feedly_config.feeds[1]['feed_name'] == "CERTs"
        assert mock_feedly_config.feeds[1]['stream_id'] == "efefefef"
        assert mock_feedly_config.article_count == 100
        assert mock_feedly_config.fetch_all == True
        assert mock_feedly_config.hours_ago == 24
    
    def test_feedly_config_initialization_invalid_article_count(self, load_env_vars):
        """
        Test loading configuration file with invalid article count. Validating that an error is raised when a string is passed instead of an integer.
        Note: Initializing the ConfigsManager depends on both envs vars (for MongoDB) and a config file (for alerts sources).
        This coupling is part of the intended design, to keep the interface of the ConfigsManager class simple.
        Here we are just testing a misconfig of the file - we provide the correct env vars using the load_env_vars fixture from conftest.py.
        """
        ConfigsManager.reset() # Singleton reset before and after to avoid state leakage.
        expected_error_message = "Input should be a valid integer, unable to parse string as an integer"
        with pytest.raises(_pydantic_core.ValidationError) as exc_info:
            config_manager = ConfigsManager('tests/unit/data_accessors/config/mock_alerts_sources_invalid_article_count.yaml')
        assert expected_error_message in str(exc_info.value)

    def test_feedly_config_initialization_invalid_access_token(self, load_env_vars):
        """
        Test loading configuration file with an access token that's empty. Validating that an error is raised when an empty string is passed in the config file.
        Note: Initializing the ConfigsManager depends on both envs vars (for MongoDB) and a config file (for alerts sources).
        This coupling is part of the intended design, to keep the interface of the ConfigsManager class simple.
        Here we are just testing a misconfig of the file - we provide the correct env vars using the load_env_vars fixture from conftest.py.
        """
        ConfigsManager.reset() # Singleton reset before and after to avoid state leakage.
        expected_error_message = "String should have at least 1 character"
        with pytest.raises(_pydantic_core.ValidationError) as exc_info:
            config_manager = ConfigsManager('tests/unit/data_accessors/config/mock_alerts_sources_invalid_access_token.yaml')
        assert expected_error_message in str(exc_info.value)
    
    def test_create_connection_with_supported_config(self, mock_feedly_dao):
        """Test creating a connection with a supported configuration class."""
        assert isinstance(mock_feedly_dao, FeedlyDAO)

    def test_create_connection_with_unsupported_config(self):
        """Test creating a connection with an unsupported configuration class."""
        unsupported_config_instance = UnsupportedConfig()

        with pytest.raises(ValueError) as exc_info:
            FetcherFactory.create_connection(unsupported_config_instance)

        assert "Invalid config type" in str(exc_info.value)
        assert "Expected one of the supported configurations" in str(exc_info.value)

    # Currently the get_dao method is not being used, but it's good to have a test for it in case it's needed in the future.
    def test_get_feedly_dao_valid(self, mock_feedly_dao):
        """Test getting a DAO with valid configuration."""
        assert isinstance(mock_feedly_dao, FeedlyDAO)

    # Currently the get_dao method is not being used, but it's good to have a test for it in case it's needed in the future.
    def test_get_dao_invalid_config_type(self):
        """Test getting a DAO with an invalid configuration type."""
        with pytest.raises(ValueError) as exc_info:
            FetcherFactory.create_connection("False configuration")
        assert "Invalid config type. Expected one of the supported configurations: " in str(exc_info.value)



class TestFeedlyDao:
    def test_fetch_alerts_success(self, mocker, mock_feedly_dao, mock_feedly_data, mock_feedly_config):
        # Setup: intercept the HTTP request to return successful response stub data.
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': mock_feedly_data,
            'continuation': None
        }
        mock_get = mocker.patch('data_accessors.fetchers.feedly.requests.get', return_value=mock_response)

        # Execute: call the fetch_alerts method with the mocked HTTP response.
        alerts = mock_feedly_dao.fetch_alerts()

        # Assert for some datapoints.
        assert "New PoC for Crit Vulnerabilities " in [a['title'] for a in alerts]
        assert "Microsoft paid Tenable a bug bounty for an Azure flaw it says doesn't need a fix, just better documentation" in [a['title'] for a in alerts]

        # In the mocked data, each stream provided should return the same number of alerts.
        stream_count = len(mock_feedly_config.feeds)
        assert len(alerts) == len(mock_feedly_data) * stream_count

        # Assert the number of times requests.get was called.
        assert mock_get.call_count == stream_count

        # Assert that raise_for_status was called once for each call to requests.get
        assert mock_response.raise_for_status.call_count == stream_count

def test_fetch_alerts_with_continuation(mocker, mock_feedly_dao):
    # Setup: create responses for two pages
    responses = [
        mocker.MagicMock(status_code=200, json=lambda: {
            'items': [{'id': '1', 'title': 'Article 1'}],
            'continuation': 'continue123'
        }),
        mocker.MagicMock(status_code=200, json=lambda: {
            'items': [{'id': '2', 'title': 'Article 2'}],
            'continuation': None
        })
    ]
    
    # Mock requests.get to return different responses in sequence
    mock_get = mocker.patch('data_accessors.fetchers.feedly.requests.get', side_effect=responses)

    # Execute
    alerts = mock_feedly_dao.fetch_alerts()

    # Assert
    assert len(alerts) == 2
    assert alerts[0]['title'] == 'Article 1'
    assert alerts[1]['title'] == 'Article 2'
    assert mock_get.call_count == 2

# ToDo: [2024-06-27, yonahcitron] Read through this again to better understand the mock_response.raise_for_status behaviour.
def test_fetch_alerts_network_failure(mocker, mock_feedly_dao):
    # Setup: Create a MagicMock for the response object
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status.side_effect = Exception("Network failure")

    # Patch requests.get to return the mock response
    mock_get = mocker.patch('data_accessors.fetchers.feedly.requests.get', return_value=mock_response)

    # Execute: Try to fetch alerts and expect an exception to be raised
    with pytest.raises(Exception) as excinfo:
        mock_feedly_dao.fetch_alerts()

    # Assertions: Check the content of the raised exception
    assert 'Network failure' in str(excinfo.value)
    # Verify that raise_for_status was called once
    mock_response.raise_for_status.assert_called_once()
    # Optionally, verify that requests.get was called once
    mock_get.assert_called_once()