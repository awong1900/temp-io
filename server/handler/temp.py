#!/usr/bin/env python
# coding=utf-8
from tornado import gen
from tornado.log import gen_log
from tornado.escape import json_decode
from base import BaseHandler
from lib import wio
from lib.utils import jsonify

class TempHandler(BaseHandler):
    """docstring for TempHandler."""
    @gen.coroutine
    def get(self, uid):
        docs = yield self.db_temp.get_all_temp_by_uid(uid)
        datas = [jsonify(doc) for doc in docs]
        for data in datas[:]:
            data.pop('_id')
        self.write({"temps": datas})
        
        
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
    @gen.coroutine
    def get(self, uid, tid):
        # TODO: (ten) authenticated uid is correct?
        result = yield self.db_temp.get_temp(tid)
        if result is None:
            self.finish()
            return
        data = jsonify(result)
        data.pop('_id')
        self.write(data)
        
    @gen.coroutine
    def patch(self, uid, tid):
        # TODO: (ten) authenticated uid is correct?
        data = json_decode(self.request.body)
        print data
        result = yield self.db_temp.update_temp(tid, data)
        data = jsonify(result)
        data.pop('_id')
        self.write(data)
        
    @gen.coroutine
    def delete(self, uid, tid):
        # TODO: (ten) authenticated uid is correct?
        yield self.db_temp.del_temp(tid)
        self.set_status(204)
        self.finish()
    
class TempsHandler(BaseHandler):
    """docstring for TempsHandler."""
    @gen.coroutine
    def get(self):
        docs = yield self.db_temp.get_all_temp()
        datas = [jsonify(doc) for doc in docs]
        for data in datas[:]:
            data.pop('_id')
        self.write({"temps": datas})
