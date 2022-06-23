from pymongo import MongoClient
import os

def get_mongo_client():
    host = os.environ['MONGODB_HOST']
    user = os.environ['MONGODB_USERNAME']
    pwd = os.environ['MONGODB_PASSWORD']
    client = MongoClient(host, 27017, username=user, password=pwd)
    return client