#!/usr/bin/env python
# coding=utf-8
from tornado import gen
from tornado.log import gen_log
from base import BaseHandler
from lib import wio
from lib.utils import jsonify

class TempHandler(BaseHandler):
    """docstring for TempHandler."""
    def get(self, uid):
        pass
        
    @gen.coroutine
    def post(self, uid):
        try:
            thing = yield wio.add_thing()
        except Exception as e:
            gen_log.error(e)
            raise
        document = {
            "uid": uid,
            "id": thing['id'],
            "key": thing['key'],
            "online": thing['online'],
            "name": "",
            "description": "",
            "private": True,
            "gps": "",
            "picture_url": ""
        }
        result = yield self.db_temp.add_temp(thing['id'], document)
        # self.set_header("Content-Type", "application/json")
        data = jsonify(result)
        data.pop('_id')
        self.write(data)

        
class TempIdHandler(BaseHandler):
    """docstring for TempIdHandler."""
    pass
    
    
class TempsHandler(BaseHandler):
    """docstring for TempsHandler."""
    pass
