from pymongo import MongoClient
import certifi

class AtlasClient():
    def __init__(self, atlas_uri, dbname):
        self.mongodb_client = MongoClient(atlas_uri, tlsCAFile=certifi.where())
        self.database = self.mongodb_client[dbname]  
    
    ## A quick way to test if we can connect to Atlas instance
    def ping (self):
        self.mongodb_client.admin.command('ping')

    def get_collection (self, collection_name):
        collection = self.database[collection_name]
        return collection

    def find (self, collection_name, filter = {}, limit=0):
        collection = self.database[collection_name]
        items = list(collection.find(filter=filter, limit=limit))
        return items