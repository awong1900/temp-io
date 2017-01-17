#!/usr/bin/env python
# coding=utf-8
import json
import os
from tornado import gen
from tornado.log import gen_log
from lib.wioapi import WioAPI
from utils import get_base_dir


class Wio(WioAPI):
    """Async http access from wio server."""
    def __init__(self, access_token=None):
        super(Wio, self).__init__(access_token)

    @gen.coroutine
    def add_thing(self, body=None):
        body = body or {"name": "anonymous"}
        try:
            thing = yield self.api('/v1/nodes/create', body=body, method="POST")
        except Exception as e:
            gen_log.error(e)
            raise
        raise gen.Return({
            "id": thing['node_sn'],
            "key": thing['node_key'],
        })

    @gen.coroutine
    def get_all_thing(self):
        try:
            node_list = yield self.api('/v1/nodes/list', method="GET")
        except Exception as e:
            gen_log.error(e)
            raise
        things = []
        for node in node_list['nodes']:
            thing = {
                "id": node['node_sn'],
                "online": node['online']
            }
            things.append(thing)

        raise gen.Return(things)

    @gen.coroutine
    def del_thing(self, tid):
        try:
            yield self.api('/v1/nodes/delete', body={"node_sn": tid}, method="POST")
        except Exception as e:
            gen_log.error(e)
            raise

    @gen.coroutine
    def add_ota(self, board_type_id):
        path = os.path.abspath(get_base_dir() + "/board.json")
        with open(path, 'r') as f:
            board_json = json.load(f)
            board = board_json[board_type_id-1]
        try:
            body = board['config']
            result = yield self.api('/v1/ota/trigger', body=body, method="POST",
                                    headers={"Content-Type": "application/json"})
        except Exception as e:
            gen_log.error(e)
            raise
        raise gen.Return({
            "status": result['ota_status'],
            "status_text": result['ota_msg']
        })

    @gen.coroutine
    def get_ota(self):
        """Get ota status from wio server, Long polling

        {"ota_msg": "Building the firmware...", "ota_status": "going"}
        {"ota_msg": "Notifying the node...[0]", "ota_status": "going"}
        {"ota_msg": "Notifying the node...[1]", "ota_status": "going"}  # try again
        {"ota_msg": "Firmware updated.", "ota_status": "done"}
        """
        try:
            result = yield self.api('/v1/ota/status', method="GET")
        except Exception as e:
            gen_log.error(e)
            raise
        raise gen.Return({
            "status": result['ota_status'],
            "status_text": result['ota_msg']
        })

    @gen.coroutine
    def get_activation(self, thing_id):
        try:
            node_list = yield self.api('/v1/nodes/list', method="GET")
        except Exception as e:
            gen_log.error(e)
            raise
        for node in node_list['nodes']:
            if node['node_sn'] == thing_id:
                if node['online'] is True:
                    raise gen.Return(True)
                else:
                    raise gen.Return(False)
        raise Exception("Not this thing on wio server")

    @gen.coroutine
    def get_temp(self, board_type_id):
        path = os.path.abspath(get_base_dir() + "/board.json")
        with open(path, 'r') as f:
            board_json = json.load(f)
            board = board_json[board_type_id-1]
        try:
            result = yield self.api(board['temp_api'], method="GET", request_timeout=5)
            temp = result['celsius_degree']
        except Exception as e:
            gen_log.error(e)
            raise

        raise gen.Return(temp)

    @gen.coroutine
    def sleep(self, seconds, board_type_id):
        path = os.path.abspath(get_base_dir() + "/board.json")
        with open(path, 'r') as f:
            board_json = json.load(f)
            board = board_json[board_type_id-1]
        try:
            yield self.api('{}/{}'.format(board['sleep_api'], seconds), method="POST")
        except Exception as e:
            gen_log.error(e)
            raise
