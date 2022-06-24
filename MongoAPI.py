import os
from pydoc import doc
from dotenv import load_dotenv
from pymongo import MongoClient
import logging as log

load_dotenv()
DATABASE = os.getenv('DATABASE')

class MongoAPI:
  def __init__(self, data):
    self.client = MongoClient(os.getenv('MONGODB_URI'))  
  
    database = DATABASE
    collection = data['collection']
    cursor = self.client[database]
    self.collection = cursor[collection]
    self.data = data
    log.info(f'MongoDB Python Connector Initialized')
  
  def readAll(self):
    documents = self.collection.find()
    output = [{item: data[item] for item in data if item != '_id'} for data in documents]
    log.info(f'Reading All Documents')
    return output

  def readOne(self):
    filt = self.data['Filter']
    document = self.collection.find_one(filt)
    output = {item: document[item] for item in document if item != '_id'}
    log.info(f'Reading Document, id: {document["_id"]}')
    return output

  def readAllGameInfo(self):
    documents = self.collection.find()
    output = [document['gameInfo'] for document in documents]
    log.info(f'Reading All games info')
    return output

  def readOneGameInfo(self):
    filt = self.data['Filter']
    document = self.collection.find_one(filt)
    output = document['gameInfo']
    log.info(f'Reading game info, id: {document["_id"]}')
    return output
  
  def create(self, data):
    new_document = data['Document']
    response = self.collection.insert_one(new_document)
    output = {item: new_document[item] for item in new_document if item != '_id'}
    output['Status'] = 'Successfully Inserted'
    output['Document_ID'] = str(response.inserted_id)
    log.info(f'Writing New Document, id: {response.inserted_id}')
    return output

  def update(self):
    log.info('Updating Data')
    filt = self.data['Filter']
    updated_data = {"$set": self.data['DataToBeUpdated']}
    response = self.collection.update_one(filt, updated_data)
    output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
    return output
  
  def playerJoin(self):
    log.info('Adding player to game')
    filt = self.data['Filter']
    updated_data = {"$addToSet": self.data['DataToBeUpdated']}
    response = self.collection.update_one(filt, updated_data)
    output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
    return output

  def playerLeave(self):
    log.info('Removing player to game')
    filt = self.data['Filter']
    updated_data = {"$pull": self.data['DataToBeUpdated']}
    response = self.collection.update_one(filt, updated_data)
    output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
    return output

  def delete(self, data):
    log.info('Deleting Data')
    filt = data['Filter']
    response = self.collection.delete_one(filt)
    output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
    return output

  def createUser(self, data):
    new_document = data['Document']
    response = self.collection.insert_one(new_document)
    output = {item: new_document[item] for item in new_document if item != '_id'}
    output['Status'] = 'Successfully Inserted'
    output['Document_ID'] = str(response.inserted_id)
    log.info(f'Writing New Document, id: {response.inserted_id}')
    return output

  def updateUser(self):
    log.info('Updating Data')
    filt = self.data['Filter']
    updated_data = {"$set": self.data['DataToBeUpdated']}
    response = self.collection.update_one(filt, updated_data)
    output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
    return output
  
  def deleteUser(self, data):
    log.info('Deleting Data')
    filt = data['Filter']
    response = self.collection.delete_one(filt)
    output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
    return output
