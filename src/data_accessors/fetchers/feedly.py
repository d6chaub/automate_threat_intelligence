import logging
import os

import requests
import yaml
from pydantic import constr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .abstract import DataFetcher
from config_managers.secrets_manager import SecretsManager

logging.basicConfig(level=logging.INFO)

# ToDo: Add documentation properly:
#access_token (str): Personal Access Token for authenticating with the Feedly API.
#streams (list[str]): List of stream IDs from which to fetch feeds.
#article_count (int): Number of articles to fetch from each stream.
#url (str): URL to the Feedly API.
#headers (dict): Headers to be included in the request to the Feedly API.
class FeedlyConfig(BaseSettings):
    """
    Configuration for connecting to the Feedly API.

    Attributes:
        model_config (SettingsConfigDict): Environment variable format for the configuration.
        access_token (str): Personal Access Token for authenticating with the Feedly API.
        feedly_sources (list[dict]): List of dictionaries, each containing a stream ID and the name of the feed associated with it.
        article_count (int): Number of articles to fetch from each stream.
        fetch_all (bool): If True, continue fetching until no more articles are available.
        hours_ago (int): Unix timestamp to fetch articles newer than this time. None to ignore.
    """
    model_config: SettingsConfigDict = SettingsConfigDict(env_prefix="FEEDLY_")
    article_count: int
    fetch_all: bool
    hours_ago: int
    feeds: str = ''
    access_token: str = ''


    def model_post_init(self, __context): # Override the default post_init method to load configs from file and secrets.
        def _validate_source_config(config: dict):
            if 'feedly_sources' not in config:
                raise ValueError('Required feedly_sources key not found in the configuration file')
            sources_config = config['feedly_sources']
            for item in sources_config:
                if not isinstance(item, dict):
                    raise ValueError('Each item in feeds must be a dictionary')
                required_keys = {'feed_name', 'stream_id'}
                if not required_keys.issubset(item.keys()):
                    raise ValueError(f"Each dictionary must contain the keys: {required_keys}")
        def load_ingestion_source_config():
            alerts_config_path = os.getenv('ALERTS_CONFIG_PATH', 'alerts_sources.yaml') # Default to file in root of az func folder if not set.
            if not os.path.exists(alerts_config_path):
                raise FileNotFoundError(f'Configuration file not found at path: {alerts_config_path}')
            with open(alerts_config_path, 'r') as file:
                config = yaml.safe_load(file)
            _validate_source_config(config)
            self.feeds = config['feedly_sources']
        def load_feedly_access_token():
            if os.getenv("IS_LOCAL") == "True":
                self.access_token = os.getenv("FEEDLY_ACCESS_TOKEN")
                return
            self.access_token = SecretsManager().get_secret_value('feedly-access-token')
        load_ingestion_source_config()
        load_feedly_access_token()
        
        # use default azure authentication to get the access token from keyvault.
    

class FeedlyDAO(DataFetcher):
    """Concrete implementation of DataFetcher to fetch data from Feedly."""

    def __init__(self, config: FeedlyConfig):
        """
        Initialize the FeedlyDAO with necessary parameters.
        
        Args:
            config (FeedlyConfig): Configuration object containing parameters for the Feedly client.
        
        """
        # Unpack the config object.
        self.access_token = config.access_token
        self.feeds = config.feeds
        self.article_count = config.article_count
        self.fetch_all = config.fetch_all
        self.hours_ago = config.hours_ago

        self.headers: dict = {'Authorization': f'Bearer {self.access_token}'}
        # Print first and last 2 chars of the access token for debugging purposes.
        logging.info('Access token: %s...%s', self.access_token[:2], self.access_token[-2:])

    def fetch_alerts(self) -> dict:
        """
        Fetches data from Feedly based on the initialized streams.
        Returns:
            dict[str, str]: Parsed data fetched from Feedly.
        """
        # And then call fetch_articles() to get the articles.
        logging.info('Fetching data from Feedly, from the following feeds:')
        logging.info([mapping['feed_name'] for mapping in self.feeds])
        for i, mapping in enumerate(self.feeds):
            logging.info('%d. %s', i, mapping['feed_name'])
        logging.info('\n')

        alerts_all_streams: list[dict] = []

        # Fetch all articles from each pre-configured stream.
        for mapping in self.feeds:
            stream_alerts: list[dict] = self._fetch_articles_from_stream(mapping)
            alerts_all_streams.extend(stream_alerts)
            logging.info('\n*After fetching all alerts from stream %s, the running total of alerts from all stream fetched is: %d*\n', mapping['feed_name'], len(alerts_all_streams))

        logging.info('\n\n**After fetching all alerts from all streams, the final count of alerts fetched is: %d**\n\n', len(alerts_all_streams))

        return alerts_all_streams

    def _fetch_articles_from_stream(
            self,
            stream_feed_mapping: dict[str, str],
            fetch_all: bool = False,
            last_timestamp: int | None = None
        ) -> list[dict]:
        """
        Fetch articles from a URL, optionally filtering by timestamp and handling pagination.
    
        Parameters:
        - stream_feed_mapping (dict[str, str]): Mapping of a Feedly stream ID to the name of the feed associatated with it.
        - fetch_all (bool): If True, continue fetching until no more articles are available.
        - last_timestamp (int | None): Unix timestamp to fetch articles newer than this time. None to ignore.
    
        Returns:
        - list[dict]: A list of articles, each represented as a dictionary.
        """

        
        feed_name: str = stream_feed_mapping['feed_name']
        stream_id: str = stream_feed_mapping['stream_id']
        stream_url: str = f'https://feedly.com/v3/streams/contents?streamId={stream_id}&count={self.article_count}'

        all_articles: list[dict] = []
        continuation: str | None = None

        logging.info('Initializing fetch of articles from feed: "%s"', feed_name)
        logging.info('')

        while True:
            params: dict = {'count': self.article_count}
            if last_timestamp is not None:
                params['newerThan'] = last_timestamp
                logging.debug('Fetching articles newer than timestamp: %s', last_timestamp)
            if continuation is not None:
                params['continuation'] = continuation
                logging.debug('Fetching next batch of articles with continuation: %s', continuation)

            response = requests.get(stream_url, headers=self.headers, params=params)
            logging.debug('Response status code of batch request to feed: %s', response.status_code)
            response.raise_for_status()
            
            response_dict = response.json()
            logging.info('Fetched batch of %d articles from feed: "%s"', len(response_dict.get('items', [])), feed_name)


            all_articles.extend(response_dict.get('items', []))
            logging.info('Running total of articles fetched from feed "%s" is: %d articles', feed_name, len(all_articles))
            continuation = response_dict.get('continuation')
            if not fetch_all or continuation is None:
                break
        
        logging.info('Finished fetching articles from feed "%s"', feed_name)
        logging.info('Total number of articles fetched from feed %s is: %d articles', feed_name, len(all_articles))

        return all_articles