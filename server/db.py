#!/usr/bin/env python
# coding=utf-8

import motor
from datetime import datetime
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
        result = yield self.db.user.find_one({'id': uid})
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
    def add_temp(self, tid, document):
        try:
            result = yield self.db.thing.find_one({'id': tid})
            if result is None:
                document['updated_at'] = datetime.utcnow()
                document['created_at'] = datetime.utcnow()
                yield self.db.thing.insert_one(document)
            else:
                document['updated_at'] = datetime.utcnow()
                yield self.db.thing.update_one({'id': tid}, {'$set': document})
        except Exception as e:
            gen_log.error(e)
            
        result = yield self.db.thing.find_one({'id': tid})
        raise gen.Return(result)
    
    @gen.coroutine
    def update_temp(self, tid, document):
        result = yield db.thing.update_one({'id': tid}, {'$set': document})
        new_doc = yield db.thing.find_one({'id': tid})
        raise gen.Return(new_doc)
    
    @gen.coroutine
    def get_temp(self, tid):
        result = yield self.db.thing.find_one({'id': tid})
        raise gen.Return(result)
        
    @gen.coroutine
    def get_all_temp_by_uid(self, uid):
        cursor = db.thing.find({'uid': uid}).sort('updated_at')
        raise gen.Return([document for document in (yield cursor.to_list(length=100))])
        
    @gen.coroutine
    def del_temp(self, tid):
         yield db.thing.delete_many({'id': tid})
        
    @gen.coroutine
    def get_all_temp(self):
        cursor = db.thing.find({}).sort('updated_at')
        raise gen.Return([document for document in (yield cursor.to_list(length=100))])  # FIXME: ten, list length, just public
