#!/usr/bin/env python
# coding=utf-8

import motor
from datetime import datetime
from bson.objectid import ObjectId
from tornado import gen
from tornado.log import gen_log
from config import mongodb as mdb

uri = "mongodb://{}:{}@{}:{}/temp_io".format(
        mdb['user'], mdb['password'], mdb['host'], mdb['port'])
db = motor.motor_tornado.MotorClient(uri).temp_io


class Db(object):
    """docstring for Db."""
    def __init__(self):
        self.db = db


class User(Db):
    """docstring for user."""
    def __init__(self):
        super(User, self).__init__()

    @gen.coroutine
    def get_user_by_uid(self, uid):
        result = yield self.db.user.find_one({'id': uid}, {'_id': 0})
        raise gen.Return(result)

    @gen.coroutine
    def add_user(self, uid, document):
        try:
            result = yield self.db.user.find_one({'id': uid})
            if result is None:
                yield self.db.user.insert_one(document)
            else:
                yield self.db.user.update_one({'id': uid}, {'$set': document})
        except Exception as e:
            gen_log.error(e)

    def update_user(self, **kwargs):
        pass

    @gen.coroutine
    def get_user_by_token(self, token):
        result = yield self.db.user.find_one({'tokens.token': token})
        raise gen.Return(result)
            
    @gen.coroutine
    def is_expire(self, token):
        # TODO: (ten), compare 0 or cur_time
        result = yield self.db.user.find_one({'tokens.token': token})
        raise gen.Return(result)


class Temp(Db):
    """docstring for temp."""
    def __init__(self):
        super(Temp, self).__init__()
        
    @gen.coroutine
    def add_temp(self, document):
        result = yield self.db.temp.insert_one(document)
        result = yield self.db.temp.find_one({"_id": ObjectId(result.inserted_id)}, {"_id": 0, 'ota': 0})
        raise gen.Return(result)
    
    @gen.coroutine
    def update_temp(self, tid, document):
        yield db.temp.update_one({'id': tid}, {'$set': document})
        result = yield db.temp.find_one({'id': tid}, {'_id': 0, 'ota': 0})
        raise gen.Return(result)
    
    @gen.coroutine
    def get_temp(self, tid):
        result = yield self.db.temp.find_one({'id': tid}, {"_id": 0, 'ota': 0})
        raise gen.Return(result)
        
    @gen.coroutine
    def get_all_temp_by_uid(self, uid):
        cursor = db.temp.find({'uid': uid}, {"_id": 0, 'ota': 0}).sort('updated_at')
        raise gen.Return([document for document in (yield cursor.to_list(length=100))])
        
    @gen.coroutine
    def del_temp(self, tid):
        yield db.temp.delete_many({'id': tid})
        
    @gen.coroutine
    def get_all_public_temp(self):
        cursor = db.temp.find({"private": False}, {'_id': 0, 'ota': 0}).sort('updated_at')
        raise gen.Return([document for document in (yield cursor.to_list(length=100))])  # FIXME: ten, list length

    @gen.coroutine
    def update_ota(self, tid, document):
        yield db.temp.update_one({'id': tid}, {'$set': {"ota": document}})
        new_doc = yield db.temp.find_one({'id': tid}, {'_id': 0, 'ota': 1})
        raise gen.Return(new_doc.get('ota'))

    @gen.coroutine
    def get_ota(self, tid):
        result = yield db.temp.find_one({'id': tid}, {'_id': 0, 'ota': 1})
        raise gen.Return(result.get('ota') if result else None)


class Temperature(Db):
    """DB operation for temperature history"""
    def __init__(self):
        super(Temperature, self).__init__()

    @gen.coroutine
    def update_temperature(self, tid, document):
        result = yield self.db.temperature.find_one({"tid": tid})
        if result is None:
            yield self.db.temperature.insert_one({"tid": tid})
        yield db.temperature.update_one({'tid': tid}, {'$push': {"temperatures": document}})

    @gen.coroutine
    def get_all_temperature_by_tid(self, tid):
        result = yield self.db.temperature.find_one({"tid": tid}, {"_id": 0, "temperatures": 1})
        raise gen.Return(result.get('temperatures') if result else [])
