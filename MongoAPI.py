import os
from dotenv import load_dotenv
from pymongo import MongoClient
#import logging as log

load_dotenv()
DATABASE = os.getenv('DATABASE')

class MongoAPI:
  def __init__(self, collection='ping'):
    self.client = MongoClient(os.getenv('MONGODB_URI'))
    self.cursor = self.client[DATABASE]
    self.collection = self.cursor[collection]
  
  def ping(self):
    output = self.cursor.command('ping')
    return output


  def create(self, new_document):
    self.collection.insert_one(new_document)
    output = {item: new_document[item] for item in new_document if item != '_id'}
    output['Status'] = 'New Document Successfully Inserted'
    return output


  def delete(self, filt):
    response = self.collection.delete_one(filt)
    output = { 'Status': 'Document Successfully Deleted', 'Code':204 } if response.deleted_count > 0 else {'Status': 'Document not found', 'Code': 404}
    return output


  def readMany(self, filt={}):
    documents = self.collection.find(filt)
    output = [{item: data[item] for item in data if item != '_id'} for data in documents]
    return output


  def readOne(self, filt):
    document = self.collection.find_one(filt)
    if (document == None):
      return {'Status': 'Document not found', 'Code': 404}
    output = {item: document[item] for item in document if item != '_id'}
    return output
  

  def update(self, filt, dataToBeUpdated):
    updated_data = {"$set": dataToBeUpdated}
    response = self.collection.update_one(filt, updated_data)
    output = {'Status': 'Document Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
    return output
    