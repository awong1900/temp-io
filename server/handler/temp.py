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
    @web.authenticated
    def get(self, uid, tid):
        # TODO: (ten) authenticated uid is correct?
        result = yield self.db_temp.get_temp(tid)
        if result is None:
            gen_log.error("Not this temp")
            self.set_status(400)
            self.finish({"error": "Not this temp"})
            return

        wio = Wio(self.current_user['token'])
        try:
            thing_list = yield wio.get_all_thing()
        except Exception as e:
            gen_log.error(e)
            return
        data = jsonify(result)
        for thing in thing_list:
            if thing["id"] == data["id"]:
                data["online"] = thing["online"]
        self.finish(data)
        
    @gen.coroutine
    @web.authenticated
    def patch(self, uid, tid):
        # TODO: (ten) authenticated uid is correct?
        data = json_decode(self.request.body)
        # TODO: limit input field
        if data.get('open'):
            if data.get('activated'):
                self.temp_task.add_in_tasks(tid)
            else:
                gen_log.error("Not activated!")
                self.set_status(400)
                self.finish({"error": "Not activated!"})
                return
        result = yield self.db_temp.update_temp(tid, data)
        if result is None:
            self.set_status(400)
            self.finish({"error": "Not found this temp"})
            return
        data = jsonify(result)
        self.finish(data)
        
    @gen.coroutine
    @web.authenticated
    def delete(self, uid, tid):
        # TODO: (ten) authenticated uid is correct?
        yield self.db_temp.del_temp(tid)
        wio = Wio(self.current_user['token'])
        try:
            yield wio.del_thing(tid)
        except Exception as e:
            gen_log.error(e)
            self.set_status(400)
            self.finish({"error": "del_thing error"})
            return
        self.set_status(204)
        self.finish()

    @gen.coroutine
    @web.authenticated
    def post(self, uid, tid):
        data = json_decode(self.request.body)
        action_type = data.get('type')
        if action_type is None:
            gen_log.error("Need type field")
            self.set_status(400)
            self.finish({"error": "Need action_type parameter"})
            return
        if action_type == "verify-activation":
            pass
            wio = Wio(self.current_user['token'])
            try:
                activated = yield wio.get_activation(tid)
            except Exception as e:
                gen_log.error(e)
                self.set_status(400)
                self.finish({"error": "Verify activation failure."})
                return
            result = yield self.db_temp.update_temp(tid, {"activated": activated})
            print result
            self.finish(jsonify(result))


class TempsHandler(BaseHandler):
    """docstring for TempsHandler."""
    @gen.coroutine
    def get(self):
        docs = yield self.db_temp.get_all_public_temp()
        temp_list = [jsonify(doc) for doc in docs]
        self.finish({"temps": temp_list})


class TempOtaHandler(BaseHandler):
    @gen.coroutine
    @web.authenticated
    def post(self, uid, tid):
        temp = yield self.db_temp.get_temp(tid)
        if temp is None:
            gen_log.error("Not this temp")
            self.set_status(400)
            self.finish({"error": "Not this temp"})
            return

        wio = Wio(self.current_user['token'])
        try:
            result = yield wio.add_ota(temp['key'])
        except Exception as e:
            gen_log.error(e)

        # save to ota collection
        # result = yield self.db_ota.update_temp(tid, data)

        # loop to get ota status

    @gen.coroutine
    def get(self):
        # query from ota collection
        pass
