import logging
import requests
import json
from src.fetchers.client_interface import DataFetcher

class FeedlyClient(DataFetcher):
    """Concrete implementation of DataFetcher to fetch data from Feedly."""

    def __init__(self, token: str, stream_feed_mappings: list[dict[str, str]], article_count: int = 100):
        """
        Initialize the Feedly client with necessary parameters.
        
        Args:
        token (str): Personal Access Token for authenticating with the Feedly API.
        streams (list[str]): List of stream IDs from which to fetch feeds.
        article_count (int): Number of articles to fetch from each stream.
        url (str): URL to the Feedly API.
        headers (dict): Headers to be included in the request to the Feedly API.
        """
        self.token: str = token
        self.stream_feed_mappings: list[dict[str, str]] = stream_feed_mappings
        self.article_count: int = article_count
        self.headers: dict = {'Authorization': f'Bearer {token}'}

    def fetch_alerts(self) -> dict:
        """
        Fetches data from Feedly based on the initialized streams.
        Returns:
            dict[str, str]: Parsed data fetched from Feedly.
        """
        # And then call fetch_articles() to get the articles.
        logging.info('Fetching data from Feedly, from the following feeds:')
        logging.info([mapping['feed_name'] for mapping in self.stream_feed_mappings])
        for i, mapping in enumerate(self.stream_feed_mappings):
            logging.info('%d. %s', i, mapping['feed_name'])
        logging.info('\n')

        alerts_all_streams: list[dict] = []

        # Fetch all articles from each pre-configured stream.
        for mapping in self.stream_feed_mappings:
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

# Example usage:
if __name__ == '__main__':
    # Set log level
    logging.basicConfig(level=logging.INFO)

    # Read in config from config/local/feedly_config.json as a dict
    config_file_path: str = 'config/local/feedly_config.json'
    with open(config_file_path, 'r', encoding='utf-8') as file:
        config: dict = json.load(file)

    token: str = config.get('token')
    stream_feed_mappings: list[dict] = config.get('stream_feed_mappings')
    article_count: int = config.get('article_count')
    fetch_all: bool = bool(config.get('fetch_all', 'False'))
    hours_ago: bool = config.get('hours_ago')

    
    fetcher = FeedlyClient(token, stream_feed_mappings, article_count)
    logging.info('Initialized Feedly client')
    
    all_articles: dict = fetcher.fetch_alerts()

    # Get fieldnames from keys of first article
    columns = all_articles[0].keys()

    # Save dict to /data/feedly_class_data.json
    with open('data/newest_data.json', 'w', encoding='utf-8') as file:
        json.dump(all_articles, file)

    # Data Science to do:
    # Test with 'Fetch all' param and without to see what the difference is.
    # This feed seems to have more than just a summary: enterprise/shell/category/39cc9153-c695-4982-bf28-9a0afc0ab8ee
    # Test with the feeds from the call.
    # Make some sort of basic target schema / definition for the nosql db, for documents. It should include a alertId (also the article's URL)
    #       Also include things like 'Fetch Date', 'Source', etc. Make this high-level. All the document-specific stuff include in the 'alertData' field or smt for now.
    # Make a mongodb definition for indexes etc, e.g. db.articles.createIndex({ "alertId": 1 }, { unique: true }).
    # Read up on feedly api and the things that are returned for different sources etc.
    
    # Findings:
    # Only a small number of articles actually have a 'content' field. This is probably because of restricted access to the full article.

    # Code Quality to do:
    # Add logging.
    # Find a better max length for lines in python and conform to it. Read up best practices.
