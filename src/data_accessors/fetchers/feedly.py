import logging
import os

import requests
import yaml
from pydantic import constr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .abstract import DataFetcher
from config_managers.secrets_manager import SecretsManager
from models.alerts_table_document import AlertDocument, SummarizationInfo, TagsInfo
from models.enums import AggregatorPlatform

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
    feeds: str = '' # ToDo: Might be better to initialise with '= field(init=False)' rather than empty str, and then set in post_init as I am. Look into this.
    access_token: str = '' # ToDo: Might be better to initialise with '= field(init=False)' rather than empty str, and then set in post_init as I am. Look into this.


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
        logging.debug('Access token: %s...%s', self.access_token[:2], self.access_token[-2:])

    def fetch_alerts(self) -> list[AlertDocument]:
        """
        Fetches data from Feedly based on the initialized streams.
        Returns:
            list[AlertDocument]: Parsed data fetched from Feedly.
        """
        # And then call fetch_articles() to get the articles.
        logging.info('Fetching data from Feedly, from the following feeds:')
        logging.info([mapping['feed_name'] for mapping in self.feeds])
        for i, mapping in enumerate(self.feeds):
            logging.info('%d. %s', i, mapping['feed_name'])
        logging.info('\n')

        alerts_all_streams: list[AlertDocument] = []

        # Fetch all articles from each pre-configured stream.
        for mapping in self.feeds:
            stream_alerts: list[AlertDocument] = self._fetch_articles_from_stream(mapping)
            alerts_all_streams.extend(stream_alerts)
            logging.info('\n*After fetching all alerts from stream %s, the running total of alerts from all stream fetched is: %d*', mapping['feed_name'], len(alerts_all_streams))

        logging.info('\n**After fetching all alerts from all streams, the final count of alerts fetched is: %d**\n', len(alerts_all_streams))
        return alerts_all_streams

    def _fetch_articles_from_stream(
            self,
            stream_feed_mapping: dict[str, str],
            fetch_all: bool = False,
            last_timestamp: int | None = None
        ) -> list[AlertDocument]:
        """
        Fetch articles from a URL, optionally filtering by timestamp and handling pagination.
    
        Parameters:
        - stream_feed_mapping (dict[str, str]): Mapping of a Feedly stream ID to the name of the feed associatated with it.
        - fetch_all (bool): If True, continue fetching until no more articles are available.
        - last_timestamp (int | None): Unix timestamp to fetch articles newer than this time. None to ignore.
    
        Returns:
        - list[AlertDocument]: A list of articles, each represented as a dictionary.
        """

        
        feed_name: str = stream_feed_mapping['feed_name']
        stream_id: str = stream_feed_mapping['stream_id']
        stream_url: str = f'https://feedly.com/v3/streams/contents?streamId={stream_id}&count={self.article_count}'

        all_alert_docs: list[dict] = []
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
            raw_alerts = response_dict.get('items', [])
            logging.info('Fetched batch of %d articles from feed: "%s"', len(raw_alerts), feed_name)

            # Here is where I should parse the response_dict into AlertDocument objects.
            alert_docs: list[AlertDocument] = [self._deserialize_raw_alert(raw_alert) for raw_alert in raw_alerts]

            all_alert_docs.extend(alert_docs)
            logging.info('Running total of articles fetched from feed "%s" is: %d articles', feed_name, len(all_alert_docs))
            continuation = response_dict.get('continuation')
            if not fetch_all or continuation is None:
                break
        
        logging.info('Finished fetching articles from feed "%s"', feed_name)
        logging.info('Total number of articles fetched from feed %s is: %d articles', feed_name, len(all_alert_docs))

        return all_alert_docs
    

    def _deserialize_raw_alert(self, raw_alert: dict) -> AlertDocument:
        """
        Deserializes a raw alert dictionary into an AlertDocument object.
        
        Args:
            raw_alert (dict): A dictionary containing raw feedly alert data.
        
        Returns:
            AlertDocument: An instance of AlertDocument containing the deserialized data.
        """
        if raw_alert is None:
            logging.error('Error: raw_alert from Feedly Stream is None.')
            raise ValueError('Error: raw_alert from Feedly Stream is None.')
        if 'originId' not in raw_alert:
            logging.error('Error: originId not found in raw alert data.')
            raise ValueError('Error: originId not found in raw alert data.')
        # ToDo: Remember to generate the ID in the alerts db, and use the returned ID when successful to store the alert in the triage db.
        aggregator_platform = AggregatorPlatform.FEEDLY
        publication_source_url: str = raw_alert.get("canonicalUrl", raw_alert["alternate"][0]["href"]) # Error if both fields not present. # https://developers.feedly.com/reference/articlejson
        alert_data: dict = raw_alert # Intentionally enforce no schema here.
        publication_datetime: int = raw_alert["published"]
        return AlertDocument(
            aggregator_platform=aggregator_platform,
            publication_source_url=publication_source_url,
            publication_datetime=publication_datetime,
            alert_data=alert_data
        )
