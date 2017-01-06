#!/usr/bin/env python
# coding=utf-8
from datetime import datetime
from tornado.ioloop import IOLoop
from tornado import httpclient
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
            self.set_status(400)
            self.finish({"error": "Get temp is failure, {}".format(e.message)})
            return
        if thing_list is None:
            self.set_status(400)
            self.finish({"temps": []})
            return
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
            self.set_status(400)
            self.finish({"error": "Create thing is failure on Wio, {}".format(e.message)})
            return
        cur_time = datetime.utcnow()
        document = {
            "uid": uid,
            "id": thing['id'],
            "key": thing['key'],
            # "online": False,
            "board_type": 1,
            "temperature": None,
            "temperature_f": None,
            "temperature_updated_at": None,
            "read_period": 60,
            "has_sleep": True,
            "status": "",
            "status_text": "",
            "open": False,
            "activated": False,
            "name": "",
            "description": "",
            "private": False,
            "gps": "",
            "picture_url": "",
            "updated_at": cur_time,
            "created_at": cur_time
        }
        result = yield self.db_temp.add_temp(document)
        data = jsonify(result)
        self.set_status(201)
        self.finish(data)


class TempIdHandler(BaseHandler):
    """docstring for TempIdHandler."""
    @gen.coroutine
    # @web.authenticated
    def get(self, uid, tid):
        # TODO: (ten) authenticated uid is correct?
        print 4444, self.user
        if self.user and self.user.get('id') == uid:
            permission = True
        else:
            permission = False

        result = yield self.db_temp.get_temp(tid)
        if result is None:
            gen_log.error("Not this temp")
            self.set_status(400)
            self.finish({"error": "Not this temp"})
            return
        data = jsonify(result)

        if permission:
            wio = Wio(self.current_user['token'])
            try:
                thing_list = yield wio.get_all_thing()
            except Exception as e:
                gen_log.error(e)
                self.set_status(400)
                self.finish({"error": "Get thing is failure on Wio, {}".format(e.message)})
                return

            for thing in thing_list:
                if thing["id"] == data["id"]:
                    data["online"] = thing["online"]

            self.finish(data)
        else:
            value = {}
            for key in ['temperature', 'temperature_f', 'temperature_updated_at', 'updated_at', 'created_at']:
                value[key] = data[key]
            self.finish(value)
        
    @gen.coroutine
    @web.authenticated
    def patch(self, uid, tid):
        # TODO: (ten) authenticated uid is correct?
        data = json_decode(self.request.body)
        temp = yield self.db_temp.get_temp(tid)
        # TODO: limit input field
        if data.get('open'):
            if temp.get('activated'):
                self.temp_task.add_in_tasks(tid)
            else:
                self.set_status(400)
                self.finish({"error": "The temp-io is not activated!"})
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


class TempVerifyActivationHandler(BaseHandler):
    @gen.coroutine
    @web.authenticated
    def post(self, uid, tid):
        wio = Wio(self.current_user['token'])
        try:
            activated = yield wio.get_activation(tid)
        except Exception as e:
            gen_log.error(e)
            self.set_status(400)
            self.finish({"error": "Get activation is failure on Wio, {}".format(e.message)})
            return
        if activated is True:
            yield self.db_temp.update_temp(tid, {"activated": activated})
            self.set_status(204)
            self.finish()
        else:
            self.set_status(400)
            self.finish({"error": "Verify activation failure."})


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

        thing_key = temp['key']
        wio = Wio(thing_key)
        try:
            result = yield wio.add_ota()
        except Exception as e:
            gen_log.error(e)
            self.set_status(400)
            self.finish({"error": "Trigger OTA is failure."})
            return

        ota = yield self.db_temp.update_ota(tid, {"status": result['status'], "status_text": result['status_text']})
        self.set_status(202)
        self.add_header("Location", "")  # TODO, get status url
        self.finish(jsonify(ota))

        IOLoop.current().add_callback(self.get_ota, tid, thing_key)

    @gen.coroutine
    def get_ota(self, tid, thing_key):
        """Long polling on Wio v1"""
        wio = Wio(thing_key)
        while 1:
            try:
                result = yield wio.get_ota()
            except httpclient.HTTPError as e:
                if e.code == 599:
                    continue
                elif e.code == 400:
                    gen_log.error(e)
                    break
            except Exception as e:
                gen_log.error(e)
                break
            yield self.db_temp.update_ota(tid, {"status": result['status'], "status_text": result['status_text']})
            if result['status'] == "error" or result['status'] == "done":
                break

    @gen.coroutine
    def get(self, uid, tid):
        ota = yield self.db_temp.get_ota(tid)
        if ota is None:
            gen_log.error("Not ota field")
            self.set_status(400)
            self.finish({"error", "Can't found ota status."})
        self.finish(jsonify(ota))


class TempTemperaturesHandler(BaseHandler):
    @gen.coroutine
    @web.authenticated
    def get(self, uid, tid):
        result = yield self.db_temperature.get_all_temperature_by_tid(tid)
        self.finish({"temperatures": jsonify(result)})


class TempsHandler(BaseHandler):
    """docstring for TempsHandler."""
    @gen.coroutine
    def get(self):
        docs = yield self.db_temp.get_all_public_temp()
        temp_list = [jsonify(doc) for doc in docs]
        self.finish({"temps": temp_list})
