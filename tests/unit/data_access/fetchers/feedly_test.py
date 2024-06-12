import json
import pytest
from unittest.mock import patch, MagicMock
from src.data_access.fetchers.feedly import FeedlyConfig
from src.data_access.fetchers import FetcherFactory

feedly_fetcher_module = 'src.data_access.fetchers.feedly.requests.get'

def load_mock_data():
    with open('tests/unit/data_access/mock_data/feedly_mock_data.json', 'r', encoding='utf-8') as file:
        return json.load(file)

@pytest.fixture
def feedly_client():
    config: FeedlyConfig = FetcherFactory.load_config('config/local/feedly_config.json', 'Feedly')
    client = FetcherFactory.get_fetcher(config)
    mock_data = load_mock_data()
    stream_count = len(config.stream_feed_mappings)
    return client, mock_data, stream_count

@pytest.mark.usefixtures("feedly_client")
class TestFeedlyClient:
    @patch(feedly_fetcher_module)
    def test_fetch_alerts_success(self, mock_get, feedly_client):
        client, mock_data, stream_count = feedly_client
        # Setup the mock to return a successful response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': mock_data,
            'continuation': None
        }
        mock_get.return_value = mock_response

        # Execute
        alerts = client.fetch_alerts()

        # Assert for some datapoints.
        assert "New PoC for Crit Vulnerabilities " in [a['title'] for a in alerts]
        assert "Microsoft paid Tenable a bug bounty for an Azure flaw it says doesn't need a fix, just better documentation" in [a['title'] for a in alerts]

        # In the mocked data, each stream should have 2 articles.
        assert len(alerts) == stream_count * 2

        # Assert the number of times requests.get was called
        assert mock_get.call_count == stream_count

        # Assert that raise_for_status was called once for each call to requests.get
        assert mock_response.raise_for_status.call_count == stream_count

    @patch(feedly_fetcher_module)
    def test_fetch_alerts_with_continuation(self, mock_get, feedly_client):
        client, _, _ = feedly_client
        # Responses for two pages
        responses = [
            MagicMock(status_code=200, json=lambda: {
                'items': [{'id': '1', 'title': 'Article 1'}],
                'continuation': 'continue123'
            }),
            MagicMock(status_code=200, json=lambda: {
                'items': [{'id': '2', 'title': 'Article 2'}],
                'continuation': None
            })
        ]
        responses[0].raise_for_status = MagicMock()
        responses[1].raise_for_status = MagicMock()
        mock_get.side_effect = responses

        # Execute
        alerts = client.fetch_alerts()

        # Assert
        assert len(alerts) == 2
        assert alerts[0]['title'] == 'Article 1'
        assert alerts[1]['title'] == 'Article 2'
        assert mock_get.call_count == 2

    @patch(feedly_fetcher_module)
    def test_fetch_alerts_network_failure(self, mock_get, feedly_client):
        client, _, _ = feedly_client
        mock_get.side_effect = Exception("Network failure")

        with pytest.raises(Exception) as excinfo:
            client.fetch_alerts()

        assert 'Network failure' in str(excinfo.value)


# TODO: [2024-06-05, yonahcitron] Add test case for when passing multiple stream_ids.
# TODO: [2024-06-05, yonahcitron] Instead of setup function, consider using fixtures or something more modern and modular.
