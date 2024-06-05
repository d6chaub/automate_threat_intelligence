import json
import unittest
from unittest.mock import patch, MagicMock
from src.fetchers.feedly_client import FeedlyClient  # Adjusted import based on your project structure


def load_mock_data():
    with open('tests/fetchers/mock_data/feedly_mock_data.json', 'r', encoding='utf-8') as file:
        return json.load(file)
    
def load_config():
    with open('config/local/feedly_config.json', 'r', encoding='utf-8') as file:
        return json.load(file)


class TestFeedlyClient(unittest.TestCase):
    def setUp(self):
        """Prepare environment for each test."""
        self.token = 'fake_token'
        self.stream_feed_mappings = [
            {'feed_name': 'Test Feed 1', 'stream_id': '1234567890'},
            {'feed_name': 'Test Feed 2', 'stream_id': '0987654321'}
        ]
        self.client = FeedlyClient(token=self.token, stream_feed_mappings=self.stream_feed_mappings)
        self.mock_data = load_mock_data()

        config: dict = load_config()
        self.stream_count = len(config['stream_feed_mappings'])


    @patch('src.fetchers.feedly_client.requests.get')
    def test_fetch_alerts_success(self, mock_get):
        """Test fetching alerts successfully from Feedly."""
        # Setup the mock to return a successful response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200
        # TODO: [2024-06-05, yonahcitron] Adjust the response JSON based on the actual response from Feedly.
        # TODO: [2024-06-05, yonahcitron] Make a test_data/feedly_responses.json or something to use.
        # TODO: [2024-06-05, yonahcitron] Or more likely use a fixture I think and import it here (work out where best to store the fixture).
        mock_response.json.return_value = {
            'items': self.mock_data,
            'continuation': None
        }
        mock_get.return_value = mock_response

        # Execute
        alerts = self.client.fetch_alerts()

        # Assert for some datapoints.
        self.assertIn("New PoC for Crit Vulnerabilities ", [a['title'] for a in alerts])
        self.assertIn("Microsoft paid Tenable a bug bounty for an Azure flaw it says doesn't need a fix, just better documentation", [a['title'] for a in alerts])

        # In the mocked data, each stream should have 2 articles.
        self.assertEqual(len(alerts), self.stream_count * 2)


        # Assert the number of times requests.get was called
        self.assertEqual(mock_get.call_count, self.stream_count)

        # Assert that raise_for_status was called once for each call to requests.get
        self.assertEqual(mock_response.raise_for_status.call_count, self.stream_count)

    @patch('src.fetchers.feedly_client.requests.get')
    def test_fetch_alerts_with_continuation(self, mock_get):
        """Test fetching alerts handling pagination with continuation."""
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
        alerts = self.client.fetch_alerts()

        # Assert
        self.assertEqual(len(alerts), 2)
        self.assertEqual(alerts[0]['title'], 'Article 1')
        self.assertEqual(alerts[1]['title'], 'Article 2')
        self.assertEqual(mock_get.call_count, 2)

    @patch('src.fetchers.feedly_client.requests.get')
    def test_fetch_alerts_network_failure(self, mock_get):
        """Test handling of network failures during alert fetch."""
        mock_get.side_effect = Exception("Network failure")

        with self.assertRaises(Exception) as context:
            self.client.fetch_alerts()

        self.assertTrue('Network failure' in str(context.exception))

# Run the tests
if __name__ == '__main__':
    unittest.main()

# TODO: [2024-06-05, yonahcitron] Add test case for when passing multiple stream_ids.
# TODO: [2024-06-05, yonahcitron] Instead of setup function, consider using fixtures or something more modern and modular.
