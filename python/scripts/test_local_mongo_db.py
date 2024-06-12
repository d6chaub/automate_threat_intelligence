import configparser
from pymongo import MongoClient

def read_config():
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
        print('Config read. Sections are as follows:')
        print(config.sections())

        host = config['MongoDB']['host']
        port = int(config['MongoDB']['port'])
        database_name = config['MongoDB']['database']
        collection_name = config['MongoDB']['collection']

        return host, port, database_name, collection_name

    except Exception as e:
        print(f'Config couldnt be read.\n{e}')
        return None, None, None, None


def connect(host, port, database_name, collection_name):
    client = MongoClient(host, port)
    db = client[database_name]
    collection = db[collection_name]
    print(collection)
    return collection

def upsert_test(collection):
    print("Beginning upsert.")
    collection.insert_one({"name": "John Doe", "age": 30})

def read_test(collection):
    print("Beginning read test.")
    document = collection.find_one({"name": "John Doe"})
    if document:
        print("Upsert Confirmed: ", document)
    else:
        print("Upsert Not Found.")

if __name__ == "__main__":
    
    host, port, database_name, collection_name = read_config()
    collection = connect(host, port, database_name, collection_name)
    upsert_test(collection)
    read_test(collection)
    