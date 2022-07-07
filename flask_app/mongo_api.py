import time

from pymongo import MongoClient


class MongoAPI:
    """
    A class to create a connection interface between python and MongoDB

    ```

    Attributes
    ----------
    uri : str
        Connection string URI to define the connection between the application and the MongoDB instance
    dbName : str
        Name of the database to connect
    collection : str
        Name of the document collection, without collection name only ping method is available

    Methods
    -------
    ping():
        Ping the database

    create(new_document):
        Insert a new document into the collection

    delete(filt):
        Delete the first found document matching the filter parameter filt

    readMany(filt):
        Find the document matching the filter parameter filt

    readOne(filt):
        Find the first document matching the filter parameter filt

    update(filt, dataToBeUpdate)
        Update the first document matching the filter parameter filt, with the data in the parameter dataToBeUpdated
    """

    def __init__(self, collection, uri, db_name):
        self.client = MongoClient(uri)
        self.cursor = self.client[db_name]
        self.collection = self.cursor[collection]

    def ping(self):
        """
        Just ping the database connected

            Parameters:
                No parameters
            Returns:
                output (dict): JSON object with two data
                    ok (int): 1 (if anything is ok)
                    latency(ms) (int): the latency in milliseconds to ping the database
        """
        pingTime = time.perf_counter()
        output = self.cursor.command('ping')
        pongTime = time.perf_counter()
        latency = pongTime - pingTime
        output['latency(ms)'] = int(latency*10**3)
        return output

    def insert_doc(self, new_document: dict):
        """
        Insert a new document in the collection

            Parameters:
                new_document (dict): JSON object defining the document to insert
            Returns:
                output (dict): the new document plus a Status data
        """
        self.collection.insert_one(new_document)
        output = {item: new_document[item]
                  for item in new_document if item != '_id'}
        output['Status'] = 'New Document Successfully Inserted'
        return output

    def delete_doc(self, filt):
        """
        Delete one document in the collection, the first matching the filter

            Parameters:
                filt (dict): JSON object defining the filter to applicate
            Returns
                output (dict): JSON object to notify the successfulness of the deletion operation 
        """
        response = self.collection.delete_one(filt)
        return {'Status': 'Document Successfully Deleted', 'Code': 204} if response.deleted_count > 0 else {'Status': 'Document not found', 'Code': 404}
    
    
    def read_random_docs(self, n=1):
        random_docs = self.collection.aggregate(([{ "$sample": { "size": n } }]))
        return [{item: data[item] for item in data if item != '_id'} for data in random_docs]


    def read_many_docs(self, filt = None, n=0):
        """
        Find many documents in the collection matching the filter

            Parameters:
                filt (dict): JSON object defining the filter to applicate
                n (int): number of document you want (0 is equivalent to no limit)
            Returns
                output (list): list of JSON objects representing the found documents
        """
        if filt is None:
            filt = {}
        documents = self.collection.find(filt).limit(n)
        return [{item: data[item] for item in data if item != '_id'} for data in documents]

    def read_one_doc(self, filt):
        """
        Find one document in the collection, the first matching the filter

            Parameters:
                filt (dict): JSON object defining the filter to applicate
            Returns
                output (dict): JSON objects representing the found document
        """
        document = self.collection.find_one(filt)
        if document is None:
            return None
        return {item: document[item] for item in document if item != '_id'}

    def update_one_doc(self, filt, data_to_put):
        """
        Update one document in the collection, the first matching the filter

            Parameters:
                filt (dict): JSON object defining the filter to applicate
                dataToBeUpdated (dict): JSON object representing the data to be updated
            Returns
                output (dict): JSON object to notify the successfulness of the updation operation 
        """
        updated_data = {"$set": data_to_put}
        response = self.collection.update_one(filt, updated_data)
        return {'Status': 'Document Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}

    def close_db(self):
        self.client.close()
