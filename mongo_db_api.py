import os
from dotenv import load_dotenv
from flask import Flask, request, json, Response
from pymongo import MongoClient

load_dotenv()

class MongoAPI:
  def __init__(self, data):
    self.client = MongoClient(os.getenv('MONGODB_URI'))  
  
    database = data['database']
    collection = data['collection']
    cursor = self.client[database]
    self.collection = cursor[collection]
    self.data = data
  
  def read(self):
    print('Reading All Data')
    documents = self.collection.find()
    output = [{item: data[item] for item in data if item != '_id'} for data in documents]
    return output

mongo = MongoAPI({ 'database': 'ScrabbleClone', 'collection': 'users'})
print(mongo.read())