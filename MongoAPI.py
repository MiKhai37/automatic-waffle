import os
from dotenv import load_dotenv
from pymongo import MongoClient
import logging as log
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
  
  def write(self, data):
    log.info('Writing Data')
    new_document = data['Document']
    response = self.collection.insert_one(new_document)
    output = {'Status': 'Successfully Inserted',
              'Document_ID': str(response.inserted_id)}
    return output

  def update(self):
    log.info('Updating Data')
    filt = self.data['Filter']
    updated_data = {"$set": self.data['DataToBeUpdated']}
    response = self.collection.update_one(filt, updated_data)
    output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
    return output
  
  def delete(self, data):
    log.info('Deleting Data')
    filt = data['Filter']
    response = self.collection.delete_one(filt)
    output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
    return output
