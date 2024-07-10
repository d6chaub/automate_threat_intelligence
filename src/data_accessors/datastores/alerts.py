import logging

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pydantic import constr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient

from data_accessors.datastores.abstract import AlertsDAO
from models.alerts_table_document import AlertDocument


# ToDo: Add type hints to the methods in the AlertsDAO class.
class MongoConfig(BaseSettings):
    """
    Configuration for connecting to a MongoDB database using environment variables.

    Attributes:
        model_config (SettingsConfigDict): Environment variable format for the configuration.
        host (str): The host address of the MongoDB server.
        port (int): The port number on which the MongoDB server is listening.
        database (str): The name of the database to connect to.
        alerts_collection (str): The name of the collection to use for alerts.
    """
    model_config: SettingsConfigDict = SettingsConfigDict(env_prefix="MONGO_")
    host: constr(min_length=1)
    port: int
    alerts_database_id: constr(min_length=1)
    alerts_collection_id: constr(min_length=1)


class CosmosConfig(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(env_prefix="COSMOS_")
    name: constr(min_length=3)
    alerts_database_id: constr(min_length=1)
    alerts_container_id: constr(min_length=1)
    alerts_container_partition_key: constr(min_length=1)
    url: str = '' # ToDo: Might be better to initialise with '= field(init=False)' rather than empty str, and then set in post_init as I am. Look into this.

    def model_post_init(self, __context):
        self.url = f"https://{self.name}.documents.azure.com:443/"



class AlertsDAOMongo(AlertsDAO):
    """
    Data Access Object (DAO) for managing alert notifications from multiple sources,
    stored in a MongoDB collection.
    """
    # ToDo: Use the actual Alerts Entity model class to insert to DB. For now hard-coding.

    def __init__(self, config: MongoConfig, client: MongoClient):
        """
        Initializes the AlertsDAO with a MongoDB client and configuration.

        Args:
            config (MongoConfig): Configuration object containing MongoDB connection details.
            client (MongoClient): Instance of MongoClient for connecting to MongoDB.
        """
        self.client = client
        self.db = self.client[config.alerts_database_id]
        self.collection = self.db[config.alerts_collection_id]

    def _add_alert(self, alert: dict): # pragma: no cover
        return self.collection.insert_one(alert).inserted_id

    # ToDo: Add debug logging for whether an alert is already present in the database.
    # Do this for the add_alerts_if_not_exist method also.
    def add_alert_if_not_duplicate(self, alert: AlertDocument):
        """
        Adds an alert to the collection only if it does not already exist.
        The publication_source_url is either the 'canonicalUrl', or, if not
        present, the 'alternate.href' field from the alert data.
        See https://developers.feedly.com/reference/articlejson for details.
        
        Args:
            alert (dict): The alert data to be added.
        
        Returns:
            The identifier of the inserted alert, generated by the db,
            or None if the alert already exists.
        """

        def _source_url_already_present(publication_source_url):
            return bool(self.collection.find_one({"publication_source_url": publication_source_url}))

        if not _source_url_already_present(alert.publication_source_url): # Check if the url of the alert is already present in the db.
            alert_dict = alert.to_dict(without_id=True) # Exclude the id field, so it is auto-generated by the db.
            return self._add_alert(alert_dict)
        

# ToDo: SORT OUT BOTH METHODS...
    
    # Method for debugging. Not for production use, no need to test.
    def debug_list_all_dbs_and_cols(self): # pragma: no cover
        """
        Debug method to list all databases and collections in the MongoDB instance.
        """
        for db_name in self.client.list_database_names():
            db = self.client[db_name]
            print(f"Database: {db_name}")
            for collection_name in db.list_collection_names():
                print(f"  Collection: {collection_name}")
                 # print size of collections
                print(f"    Collection size: {db[collection_name].count_documents({})}")

class AlertsDAOCosmos(AlertsDAO):
    def __init__(self, config: CosmosConfig, client: CosmosClient):
        self.container_partition_key = config.alerts_container_partition_key
        self.client = client
        self.database = self.client.get_database_client(config.alerts_database_id)
        self.container = self.database.get_container_client(config.alerts_container_id)

    def _check_if_source_url_present(self, publication_source_url):
        """ 
        Checks Cosmos DB to see if the publication source URL already exists there.
        The URL is functionally a unique identifier for the alert.
        If it does exist, adding another alert with the same URL would be a duplicate.
        """
        query = "SELECT * FROM c WHERE c.publication_source_url = @url"
        parameters = [{"name": "@url", "value": publication_source_url}]
    
        items = list(self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True  # This may be required if partition key is not part of the query
        ))

        if items:
            return True
        return False


    def add_alert_if_not_duplicate(self, alert: AlertDocument):
        """
        Adds an alert to the collection only if it does not already exist.
        The publication_source_url is either the 'canonicalUrl', or, if not
        present, the 'alternate.href' field from the alert data.
        See https://developers.feedly.com/reference/articlejson for details.
        
        Args:
            alert (dict): The alert data to be added.
        
        Returns:
            The identifier of the inserted alert, generated by the db,
            or None if the alert already exists.
        """
        # ToDo: Find a better way to test this etc.
        is_duplicate: bool = self._check_if_source_url_present(alert.publication_source_url)
        if not is_duplicate:
            alert_dict = alert.to_dict(without_id=True) # Exclude the id field, so it is auto-generated by the db.  # paritionkey should be 'aggregatorPlatformName' and id should be 'contentPublicationUrl'
            cosmos_item = self.container.create_item( # Upon successful creation, the whole item is returned from cosmos by default.
                body=alert_dict,
                enable_automatic_id_generation=True 
            )
            if cosmos_item:
                return cosmos_item['id']
        return None



    # Debugging method for listing databases and collections - optional
    def debug_list_all_dbs_and_cols(self):  # pragma: no cover
        """
        Debug method to list all databases and collections in the Cosmos DB instance.
        """
        logging.info("Listing all databases and containers:")
        for db in self.client.list_databases():
            logging.info(f"Database: {db['id']}")
            database_client = self.client.get_database_client(db['id'])
            for container in database_client.list_containers():
                logging.info(f"  Container: {container['id']}")
