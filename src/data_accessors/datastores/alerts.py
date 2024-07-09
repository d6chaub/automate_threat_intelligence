import logging

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pydantic import constr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient

from data_accessors.datastores.abstract import AlertsDAO


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
    def add_alert_if_not_exists(self, alert: dict):
        """
        Adds an alert to the collection only if it does not already exist.
        
        Args:
            alert (dict): The alert data to be added.
        
        Returns:
            The identifier of the inserted alert, or None if the alert already exists.
        """

        def _origin_id_already_present(origin_id):
            return bool(self.collection.find_one({"originId": origin_id}))

        if not _origin_id_already_present(alert["originId"]):
            return self._add_alert(alert)
        
    def add_alerts_if_not_exist(self, alerts: list[dict]) -> list[int]:
        """
        Adds multiple alerts to the collection only if they do not already exist.

        Args:
            alerts (list[dict]): A list of alert data to be added.

        Returns:
            A list of identifiers for the inserted alerts.
        """
        inserted_ids = []
        for alert in alerts:
            inserted_id = self.add_alert_if_not_exists(alert)
            if inserted_id:
                inserted_ids.append(inserted_id)
        return inserted_ids


    def delete_alert(self, item_id):
        """
        Deletes an alert from the collection.

        Args:
            item_id (any): The identifier of the alert to be deleted.

        Returns:
            The result of the delete operation.
        """
        return self.collection.delete_one({"_id": item_id})

    def get_alert(self, item_id):
        """
        Retrieves a single alert from the collection by its identifier.

        Args:
            item_id (any): The identifier of the alert to be retrieved.

        Returns:
            A dictionary representing the alert data, or None if no alert is found.
        """
        return self.collection.find_one({"_id": item_id})

    def get_all_alerts(self):
        """
        Retrieves all alerts from the collection.

        Returns:
            A list of dictionaries, each representing an alert's data.
        """
        return list(self.collection.find())
    
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

    def add_alert_if_not_exists(self, alert: dict):
        try:
            # test object -- make this into a proper model class...
            db_obj = {'alertUrl': 'Feedly', 'alert_body': alert} # paritionkey should be 'aggregatorPlatformName' and id should be 'contentPublicationUrl'
            self.container.create_item(body=db_obj, enable_automatic_id_generation=True) # Disable auto_id afterwards and configure the id to be the contentPublicationUrl
        except exceptions.CosmosResourceExistsError:
            return None

    def add_alerts_if_not_exist(self, alerts: list[dict]) -> list[int]:
        inserted_ids = []
        for alert in alerts:
            inserted_id = self.add_alert_if_not_exists(alert)
            if inserted_id:
                inserted_ids.append(inserted_id)
        return inserted_ids


    def get_all_alerts(self):
        query = "SELECT * FROM c"
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        return items

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
