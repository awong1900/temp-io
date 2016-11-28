#!/usr/bin/env python
# coding=utf-8
from tornado import gen
from tornado.log import gen_log
from base import BaseHandler
from lib import wio

class TempHandler(BaseHandler):
    """docstring for TempHandler."""
    def get(self):
        pass
        
    @gen.coroutine
    def post(self):
        try:
            thing = yield wio.add_thing()
        except Exception ae e:
            gen_log.error(e)
        document = {
            "id": thing['thing_id']
            "key": thing['key']
            "online": thing['online']
            "name": ""
            "description": ""
            "name": ""
            "private": True
            "gps": ""
            "picture_url": ""
        }
        result = yield self.db_temp.add_temp(thing['thing_id'], document)
        
class TempIdHandler(BaseHandler):
    """docstring for TempIdHandler."""
    pass
    
    
class TempsHandler(BaseHandler):
    """docstring for TempsHandler."""
    pass
        
        
