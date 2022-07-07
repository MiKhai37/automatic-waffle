import os

from dotenv import load_dotenv
from flask_app.mongo_api import MongoAPI

load_dotenv()

mongo_api = MongoAPI('infos', os.getenv('MONGO_URI'), 'Testing')

def test_insert():
    insert_result = mongo_api.insert_doc({'id': 'test_id', 'test': 'test_value'})
    assert insert_result['Status'] == 'New Document Successfully Inserted'


def test_read_one():
    test_info_doc = mongo_api.read_one_doc({'id': 'test_id'})
    assert test_info_doc['test'] == 'test_value'

    inexistant_info_doc = mongo_api.read_one_doc({'id': 'inexistant_id'})
    assert inexistant_info_doc is None

def test_update():
    test_info_doc = mongo_api.read_one_doc({'id': 'test_id'})
    assert test_info_doc.get('new_key') is None

    update_result = mongo_api.update_one_doc({'id': 'test_id'}, {'new_key': 'new_value'})
    assert update_result['Status'] == 'Document Successfully Updated'
    test_info_doc = mongo_api.read_one_doc({'id': 'test_id'})
    assert test_info_doc.get('new_key') is not None

    reupdate_result = mongo_api.update_one_doc({'id': 'test_id'}, {'new_key': 'new_value'})
    assert reupdate_result['Status'] == 'Nothing was updated.'

def test_delete():
    delete_result = mongo_api.delete_doc({'id': 'test_id'})
    assert delete_result['Status'] == 'Document Successfully Deleted'

    redelete_result = mongo_api.delete_doc({'id': 'test_id'})
    assert redelete_result['Status'] == 'Document not found'
