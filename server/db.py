#!/usr/bin/env python
# coding=utf-8

import motor
from tornado import gen
from tornado.log import gen_log


db = motor.motor_tornado.MotorClient('localhost', 27017).temp-io

class User(object):
    """docstring for user."""
    def __init__(self, db):
        super(User, self).__init__()
        self.db = db
    
    @gen.coroutine
    def add_user(self, **kwargs):
        try:
            result = yield db.test_collection.insert_one(kwargs)
        except Exception as e:
            gen_log.error(e)

    def update_user(self, **kwargs):
        pass

    @gen.coroutine
    def get_user_by_token(self, token):
        result = yield self.db.user.find_one({'tokens.token':token})
        raise gen.Return(result)
            
            
class Temp(object):
    """docstring for temp."""
    def __init__(self, db):
        super(Temp, self).__init__()
        self.db = db
        
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
        
