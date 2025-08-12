from pymongo import MongoClient
from django.conf import settings

class MongoDBConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient('mongodb://localhost:27017/')
            cls._instance.db = cls._instance.client['installations_techniques']
        return cls._instance
    
    def get_collection(self, collection_name):
        return self.db[collection_name]

# Utilisation
mongo_db = MongoDBConnection()