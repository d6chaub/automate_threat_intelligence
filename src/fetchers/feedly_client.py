import logging
import requests
import json
from src.fetchers.client_interface import DataFetcher

class FeedlyClient(DataFetcher):
    """Concrete implementation of DataFetcher to fetch data from Feedly."""

    def __init__(self, token: str, stream_ids: list[str], article_count: int = 100):
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
        self.stream_ids: list[str] = stream_ids
        self.article_count: int = article_count
        self.headers: dict = {'Authorization': f'Bearer {token}'}

    def fetch_alerts(self) -> dict:
        """
        Fetches data from Feedly based on the initialized streams.
        Returns:
            dict[str, str]: Parsed data fetched from Feedly.
        """
        # And then call fetch_articles() to get the articles.
        logging.debug('Fetching data from Feedly, from the following feeds:')
        logging.debug(self.stream_ids)

        alerts_all_streams: list[dict] = []

        for stream_id in self.stream_ids:
            logging.info('Fetching articles from stream: %s', stream_id)
            stream_url: str = f'https://feedly.com/v3/streams/contents?streamId={stream_id}&count={self.article_count}'
            stream_alerts: list[dict] = self._fetch_articles_from_stream(stream_url)
            logging.info('Fetched %d articles from stream: %s', len(stream_alerts), stream_id)
            alerts_all_streams.extend(stream_alerts)
            logging.info('After extending, alerts_all_streams has %d articles', len(alerts_all_streams))

        return alerts_all_streams

    def _fetch_articles_from_stream(self, stream_url, fetch_all: bool = False, last_timestamp: int | None = None) -> list[dict]:
        """
        Fetch articles from a predefined URL, optionally filtering by timestamp and handling pagination.
    
        Parameters:
        - fetch_all (bool): If True, continue fetching until no more articles are available.
        - last_timestamp (int | None): Unix timestamp to fetch articles newer than this time. None to ignore.
    
        Returns:
        - list[dict]: A list of articles, each represented as a dictionary.
        """
        all_articles: list[dict] = []
        continuation: str | None = None

        while True:
            logging.info('Fetching articles from Feedly...')
            params: dict = {'count': self.article_count}
            if last_timestamp is not None:
                params['newerThan'] = last_timestamp
            if continuation is not None:
                params['continuation'] = continuation
                logging.debug('Fetching next page of articles with continuation: %s', continuation)

            response = requests.get(stream_url, headers=self.headers, params=params)
            logging.info('Response status code: %s', response.status_code)
            response.raise_for_status()
            
            response_dict = response.json()
            logging.info('Fetched %d articles from Feedly', len(response_dict.get('items', [])))

            all_articles.extend(response_dict.get('items', []))
            logging.info('Extended all_articles to %d articles', len(all_articles))
            continuation = response_dict.get('continuation')
            if not fetch_all or continuation is None:
                break

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

    stream_ids: list[str] = [mapping['stream_id'] for mapping in stream_feed_mappings]
    fetcher = FeedlyClient(token, stream_ids, article_count)
    logging.info('Initialized Feedly client')
    
    all_articles: dict = fetcher.fetch_alerts()
    logging.info('Fetched %d articles from Feedly', len(all_articles))

    # Get fieldnames from keys of first article
    columns = all_articles[0].keys()

    # Save dict to /data/feedly_class_data.json
    with open('data/feedly_class_data.json', 'w', encoding='utf-8') as file:
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
