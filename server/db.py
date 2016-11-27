#!/usr/bin/env python
# coding=utf-8

import motor
from tornado import gen
from tornado.log import gen_log

db = motor.motor_tornado.MotorClient('localhost', 27017).temp_io
class Db(object):
    """docstring for Db."""
    def __init__(self):
        self.db = db
        
class User(Db):
    """docstring for user."""
    def __init__(self):
        super(User, self).__init__()
    
    @gen.coroutine
    def add_user(self, id, document):
        try:
            result = yield self.db.user.find_one({'id': id})
            if result is None:
                yield self.db.user.insert_one(document)
            else:
                yield self.db.user.update_one({'id': id}, {'$set': document})
        except Exception as e:
            gen_log.error(e)

    def update_user(self, **kwargs):
        pass

    @gen.coroutine
    def get_user_by_token(self, token):
        result = yield self.db.user.find_one({'tokens.token':token})
        raise gen.Return(result)
            
            
class Temp(Db):
    """docstring for temp."""
    def __init__(self):
        super(Temp, self).__init__()
        
    def add_temp(self, **kwargs):
        pass
        
    def update_temp(self, **kwargs):
        pass
        
    def get_temp(self, **kwawrgs):
        pass
        
    def del_temp(self, **kwargs):
        pass
        
    def get_all_temp(self, **kwawrgs):
        pass
        
