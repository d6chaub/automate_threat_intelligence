import logging
from pymongo import MongoClient
from pydantic import BaseModel

# ToDo: Add type hints to the methods in the AlertsDAO class.

class MongoConfig(BaseModel):
    """
    Configuration for connecting to a MongoDB database.

    Attributes:
        host (str): The host address of the MongoDB server.
        port (int): The port number on which the MongoDB server is listening.
        database (str): The name of the database to connect to.
        alerts_collection (str): The name of the collection to use for alerts.
    """
    host: str
    port: int
    database: str
    alerts_collection: str

class AlertsDAO:
    """
    Data Access Object (DAO) for managing alert notifications from multiple sources,
    stored in a MongoDB collection.
    """

    def __init__(self, config: MongoConfig, client: MongoClient):
        """
        Initializes the AlertsDAO with a MongoDB client and configuration.

        Args:
            config (MongoConfig): Configuration object containing MongoDB connection details.
            client (MongoClient): Instance of MongoClient for connecting to MongoDB.
        """
        self.client = client
        self.db = self.client[config.database]
        self.collection = self.db[config.alerts_collection]

    def add_alert(self, alert: dict):
        return self.collection.insert_one(alert).inserted_id
    
    def add_alerts(self, alerts: list[dict]):
        return self.collection.insert_many(alerts).inserted_ids

    # ToDo: Add debug logging for whether an alert is already present in the database.
    # Do this for the add_alerts_if_not_exist method also.
    def add_alert_if_not_exists(self, alert: dict):

        def _origin_id_already_present(origin_id):
            return bool(self.collection.find_one({"originId": origin_id}))

        if not _origin_id_already_present(alert["originId"]):
            return self.add_alert(alert)
        
    def add_alerts_if_not_exist(self, alerts: list[dict]) -> list[int]:
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
    
    def debug_list_all_dbs_and_collections(self):
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
       
