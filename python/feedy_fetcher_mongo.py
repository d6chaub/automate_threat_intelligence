import sys
import time
import requests
import csv
import json
import configparser
import os
from pymongo import MongoClient

def flatten_json(d, prefix='', separator='_', max_depth=None, depth=0):
    flattened = {}

    if max_depth is not None and depth >= max_depth:
        return {prefix: d}

    if isinstance(d, dict):
        for key, value in d.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            if isinstance(value, (dict, list)):
                flattened.update(flatten_json(value, new_key, separator, max_depth, depth + 1))
            else:
                flattened[new_key] = value
    elif isinstance(d, list):
        for index, value in enumerate(d):
            new_key = f"{prefix}{separator}{index}" if prefix else str(index)
            if isinstance(value, (dict, list)):
                flattened.update(flatten_json(value, new_key, separator, max_depth, depth + 1))
            else:
                flattened[new_key] = value

    return flattened

class FeedlyFetcher:
    def __init__(self, token, stream_id, article_count):
        self.token = token
        self.stream_id = stream_id
        self.article_count = article_count
        self.url = f'https://feedly.com/v3/streams/contents?streamId={stream_id}&count={article_count}'
        self.headers = {'Authorization': f'Bearer {token}'}

    def fetch_articles(self, fetch_all=False, last_timestamp=None):
        all_articles = []
        continuation = None

        while True:
            params = {'count': self.article_count}
            if last_timestamp is not None:
                params['newerThan'] = last_timestamp
            if continuation is not None:
                params['continuation'] = continuation

            response = requests.get(self.url, headers=self.headers, params=params)
            response.raise_for_status()
            response_dict = response.json()

            all_articles.extend(response_dict.get('items', []))
            continuation = response_dict.get('continuation')
            print(f'Retrieved {len(all_articles)} articles')
            if not fetch_all or continuation is None:
                break

        return all_articles

    def save_to_csv(self, article_list, output_filename, max_depth, columns):
        if not article_list:
            print('No articles were fetched or processed. Exiting.')
            sys.exit(0)

        flattened_articles = (flatten_json(article, max_depth=max_depth) for article in article_list)
        fieldnames = columns if columns else sorted(list(set().union(*(article.keys() for article in flattened_articles))))

        os.makedirs('data', exist_ok=True)

        with open(f'data/{output_filename}.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for article in flattened_articles:
                writer.writerow({k: article[k] for k in fieldnames if k in article})

        print('Article data has been successfully saved to "article_data.csv"')

    def save_to_json(self, article_list):
        if not article_list:
            print('No articles were fetched. Exiting.')
            sys.exit(0)

        with open('article_data.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(article_list, jsonfile, ensure_ascii=False, indent=2)

        print('Article data has been successfully saved to "article_data.json"')

    def save_to_mongodb(self, article_list, host, port, database_name, collection_name, columns):
        if not article_list:
            print('No articles were fetched. Exiting.')
            sys.exit(0)

        client = MongoClient(host, port)
        db = client[database_name]
        collection = db[collection_name]

        flattened_articles = [flatten_json(article) for article in article_list]

        # Filter out unwanted keys based on the column names specified in the config file.
        filtered_articles = [
            {key: article[key] for key in columns if key in article}
            for article in flattened_articles
        ]

        collection.insert_many(filtered_articles)
        print('Article data has been successfully saved to MongoDB')

def main():
    config = configparser.ConfigParser()
    config.read('config/local/config.ini')

    feedly_config = config['Feedly']
    mongodb_config = config['MongoDB']

    token = feedly_config.get('token')
    stream_id = feedly_config.get('stream_id')
    article_count = feedly_config.getint('article_count', fallback=100)
    fetch_all = feedly_config.getboolean('fetch_all', fallback=False)
    hours_ago = feedly_config.getint('hours_ago', fallback=None)
    output_format = feedly_config.get('output_format', fallback='csv')
    output_filename = feedly_config.get('output_filename', fallback='')
    max_depth = feedly_config.getint('max_depth', fallback=3)
    columns = [column.strip() for column in feedly_config.get('columns', fallback='').split(',')]

    fetcher = FeedlyFetcher(token, stream_id, article_count)
    last_timestamp = None

    if hours_ago:
        hours_ago_ms = hours_ago * 3600 * 1000
        last_timestamp = int(time.time() * 1000) - hours_ago_ms

    all_articles = fetcher.fetch_articles(fetch_all=fetch_all, last_timestamp=last_timestamp)

    if output_format == 'csv':
        fetcher.save_to_csv(all_articles, output_filename, max_depth, columns)
    elif output_format == 'json':
        fetcher.save_to_json(all_articles)
    elif output_format == 'mongodb':
        fetcher.save_to_mongodb(
            all_articles, 
            mongodb_config['host'],
            mongodb_config.getint('port'),
            mongodb_config['database'],
            mongodb_config['collection'],
            columns
        )

if __name__ == '__main__':
    main()
