"""
tests/Modules/test_DbMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
from unittest.mock import MagicMock, patch
from db4e.Modules.DbMgr import DbMgr
from db4e.Constants.SoftwareSystems import Db4E_Record_Template

def test_dbmgr_init(config):
    db_mgr = DbMgr(config)
    assert db_mgr is not None

@patch('db4e.Modules.DbMgr.MongoClient')
def test_find_one(mock_mongo_client, config):
    # Setup mock MongoDB hierarchy
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {"foo": "bar"}

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    mock_client_instance = MagicMock()
    mock_client_instance.__getitem__.return_value = mock_db

    mock_mongo_client.return_value = mock_client_instance

    # Initialize DbMgr with the fixture code in tests/conftest.py
    db_mgr = DbMgr(config)
    assert db_mgr is not None

    # Act
    result = db_mgr.find_one("mining", {"foo": "bar"})

    # Assert
    assert result == {"foo": "bar"}
    mock_collection.find_one.assert_called_once_with({"foo": "bar"})

@patch("db4e.Modules.DbMgr.MongoClient")
def test_get_collection(mock_mongo_client, config):
    mock_collection = MagicMock()
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client_instance = MagicMock()
    mock_client_instance.__getitem__.return_value = mock_db
    mock_mongo_client.return_value = mock_client_instance

    db_mgr = DbMgr(config)
    collection = db_mgr.get_collection("mining")
    assert collection == mock_collection

@patch("db4e.Modules.DbMgr.MongoClient")
def test_insert_one(mock_mongo_client, config):
    mock_collection = MagicMock()
    mock_collection.insert_one.return_value = {"acknowledged": True}

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client_instance = MagicMock()
    mock_client_instance.__getitem__.return_value = mock_db
    mock_mongo_client.return_value = mock_client_instance

    db_mgr = DbMgr(config)
    result = db_mgr.insert_one("mining", {"doc": "test"})
    assert result == {"acknowledged": True}
    mock_collection.insert_one.assert_called_once_with({"doc": "test"})

@patch("db4e.Modules.DbMgr.MongoClient")
def test_update_one(mock_mongo_client, config):
    mock_collection = MagicMock()
    mock_collection.update_one.return_value = {"matched_count": 1}

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client_instance = MagicMock()
    mock_client_instance.__getitem__.return_value = mock_db
    mock_mongo_client.return_value = mock_client_instance

    db_mgr = DbMgr(config)
    result = db_mgr.update_one("mining", {"name": "foo"}, {"value": 42})
    assert result == {"matched_count": 1}
    mock_collection.update_one.assert_called_once_with({"name": "foo"}, {"$set": {"value": 42}})

def test_get_new_rec(config):
    db_mgr = DbMgr(config)
    result = db_mgr.get_new_rec("db4e")
    assert result == Db4E_Record_Template
