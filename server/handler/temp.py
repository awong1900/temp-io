#!/usr/bin/env python
# coding=utf-8
from datetime import datetime
from tornado import gen
from tornado import web
from tornado.log import gen_log
from tornado.escape import json_decode
from base import BaseHandler
from lib.wio import Wio
from lib.utils import jsonify


class TempHandler(BaseHandler):
    """docstring for TempHandler."""
    @gen.coroutine
    @web.authenticated
    def get(self, uid):
        wio = Wio(self.current_user['token'])
        try:
            thing_list = yield wio.get_all_thing()
        except Exception as e:
            gen_log.error(e)
        docs = yield self.db_temp.get_all_temp_by_uid(uid)
        temp_list = [jsonify(doc) for doc in docs]
        for temp in temp_list[:]:  # FIXME, need more efficiency
            for thing in thing_list:
                if thing['id'] == temp['id']:
                    temp['online'] = thing['online']
        self.finish({"temps": temp_list})

    @gen.coroutine
    @web.authenticated
    def post(self, uid):
        wio = Wio(self.current_user['token'])
        try:
            thing = yield wio.add_thing()
        except Exception as e:
            gen_log.error(e)
            raise
        cur_time = datetime.utcnow()
        document = {
            "uid": uid,
            "id": thing['id'],
            "key": thing['key'],
            # "online": False,
            "temperature": 0,
            "temperature_f": None,
            "temperature_updated_at": None,
            "read_period": 60,
            "has_sleep": True,
            "status": "",
            "status_text": "",
            "open": True,
            "activated": False,
            "name": "",
            "description": "",
            "private": True,
            "gps": "",
            "picture_url": "",
            "updated_at": cur_time,
            "created_at": cur_time
        }
        result = yield self.db_temp.add_temp(document)
        data = jsonify(result)
        self.finish(data)


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
        self.finish(data)
        
    @gen.coroutine
    def patch(self, uid, tid):
        # TODO: (ten) authenticated uid is correct?
        data = json_decode(self.request.body)
        print data
        result = yield self.db_temp.update_temp(tid, data)
        data = jsonify(result)
        data.pop('_id')
        self.finish(data)

        if data.get('activated') and data.get('open'):
            self.temp_task.add_in_tasks(tid)
        
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
        self.finish({"temps": datas})
