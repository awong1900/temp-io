#!/usr/bin/env python
# coding=utf-8
import os
import json
from datetime import datetime
from tornado.ioloop import IOLoop
from tornado import httpclient
from tornado import gen
from tornado import web
from tornado.web import HTTPError
from tornado.log import gen_log
from tornado.escape import json_decode
from base import BaseHandler
from base import UserBaseHandler
from base import TempBaseHandler
from lib.wio import Wio
from lib.utils import jsonify
from lib.utils import get_base_dir


class TempHandler(UserBaseHandler):
    """Operate API /users/:id/temps"""
    @gen.coroutine
    def get(self, uid):
        """get all temp-io devices of specific user"""
        if self.req_user and self.req_user['myself'] is True:
            wio = Wio(self.req_token)
            try:
                thing_list = yield wio.get_all_thing()
            except Exception as e:
                gen_log.error(e)
                raise HTTPError(400, "Get temp is failure, {}".format(e.message))
            if thing_list is None:
                self.set_status(200)
                self.finish({"temps": []})
                return
            docs = yield self.db_temp.get_all_temp_by_uid(uid)
            temp_list = [jsonify(doc) for doc in docs]
            for temp in temp_list[:]:  # FIXME, need more efficiency
                for thing in thing_list:
                    if thing['id'] == temp['id']:
                        temp['online'] = thing['online']
            self.finish({"temps": temp_list})
        else:
            docs = yield self.db_temp.get_all_temp_by_uid(uid)
            temp_list = []
            for doc in docs:
                if doc['private'] is False:
                    temp_list.append(jsonify(doc))
            self.finish({"temps": temp_list})

    @gen.coroutine
    @web.authenticated
    def post(self, uid):
        """create a temp-io device on server"""
        if self.req_user and self.req_user['myself'] is False:
            raise HTTPError(400, "No operation permission")
        wio = Wio(self.req_token)
        try:
            thing = yield wio.add_thing()
        except Exception as e:
            gen_log.error(e)
            raise HTTPError(400, "Create temp-io is failure on built-in Wio server, {}".format(str(e)))
        cur_time = datetime.utcnow()
        document = {
            "uid": uid,
            "id": thing['id'],
            "key": thing['key'],
            # "online": False,
            "board_type_id": 1,
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


class TempIdHandler(TempBaseHandler):
    """Operate API /users/:id/temps/:id"""
    @gen.coroutine
    def get(self, uid, tid):
        if self.req_user and self.req_user['myself'] is True:
            data = jsonify(self.temp)
            wio = Wio(self.req_token)
            try:
                thing_list = yield wio.get_all_thing()
            except Exception as e:
                gen_log.error(e)
                raise HTTPError(400, "Get thing is failure from built-in Wio server, {}".format(str(e)))

            for thing in thing_list:
                if thing["id"] == data["id"]:
                    data["online"] = thing["online"]
            self.finish(data)
        else:
            if self.temp['private'] is True:
                raise HTTPError(400, "The device is private")
            data = jsonify(self.temp)
            value = {}
            # TODO, filter output value
            for key in ['temperature', 'temperature_f', 'temperature_updated_at', 'updated_at', 'created_at']:
                value[key] = data[key]
            self.finish(value)
        
    @gen.coroutine
    @web.authenticated
    def patch(self, uid, tid):
        if self.req_user and self.req_user['myself'] is False:
            raise HTTPError(400, "No operation permission")
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
        temp = yield self.db_temp.update_temp(tid, data)
        data = jsonify(temp)
        self.finish(data)
        
    @gen.coroutine
    @web.authenticated
    def delete(self, uid, tid):
        if self.req_user and self.req_user['myself'] is False:
            raise HTTPError(400, "No operation permission")
        yield self.db_temp.del_temp(tid)
        wio = Wio(self.req_token)
        try:
            yield wio.del_thing(tid)
        except Exception as e:
            gen_log.error(e)
            raise HTTPError(400, "del_thing error, {}".format(str(e)))
        self.set_status(204)
        self.finish()


class TempVerifyActivationHandler(TempBaseHandler):
    @gen.coroutine
    @web.authenticated
    def post(self, uid, tid):
        if self.req_user and self.req_user['myself'] is False:
            raise HTTPError(400, "No operation permission")
        wio = Wio(self.req_token)
        try:
            activated = yield wio.get_activation(tid)
        except Exception as e:
            gen_log.error(e)
            raise HTTPError(400, "Get activation is failure on built-in Wio server, {}".format(str(e)))
        if activated is True:
            yield self.db_temp.update_temp(tid, {"activated": activated})
            self.set_status(204)
            self.finish()
        else:
            self.set_status(400)
            self.finish({"error": "Verify activation failure."})


class TempOtaHandler(TempBaseHandler):
    @gen.coroutine
    @web.authenticated
    def post(self, uid, tid):
        if self.req_user and self.req_user['myself'] is False:
            raise HTTPError(400, "No operation permission")
        thing_key = self.temp['key']
        wio = Wio(thing_key)
        try:
            result = yield wio.add_ota(self.temp['board_type_id'])
        except Exception as e:
            gen_log.error(e)
            raise HTTPError(400, "Trigger OTA is failure, {}".format(str(e)))

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
    @web.authenticated
    def get(self, uid, tid):
        if self.req_user and self.req_user['myself'] is False:
            raise HTTPError(400, "No operation permission")
        ota = yield self.db_temp.get_ota(tid)
        if ota is None:
            gen_log.error("Not ota field")
            raise HTTPError(400, "Can't found ota status.")
        self.finish(jsonify(ota))


class TempTemperaturesHandler(TempBaseHandler):
    @gen.coroutine
    def get(self, uid, tid):
        if self.temp['private'] is True:
            raise HTTPError(400, "The device is private")
        result = yield self.db_temperature.get_all_temperature_by_tid(tid)
        self.finish({"temperatures": jsonify(result)})


class TempsHandler(BaseHandler):
    """docstring for TempsHandler."""
    @gen.coroutine
    def get(self):
        docs = yield self.db_temp.get_all_public_temp()
        temp_list = [jsonify(doc) for doc in docs]
        self.finish({"temps": temp_list})


class BoardsHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        path = os.path.abspath(get_base_dir() + "/board.json")
        with open(path) as f:
            boards = json.load(f)

        self.finish({"boards": boards})
