#!/usr/bin/env python
# coding=utf-8
import uuid
from tornado import gen
from tornado.log import gen_log
from lib.wioapi import WioAPI


class Wio(WioAPI):
    """docstring for Wio.
    
        Async http access from wio server.
    """
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
    def add_ota(self, thing_key):
        try:
            body = {
                "board_name": "Wio Link v1.0",  # TODO, different board do different json
                "connections": [
                    {
                        "port": "D0",
                        "sku": "101020019-ffff"
                    }
                ]
            }
            result = yield self.api('/v1/ota/trigger', query={"access_token": thing_key}, body=body, method="POST")
        except Exception as e:
            gen_log.error(e)
            raise
        raise gen.Return({
            "status": result['ota_status'],
            "status_text": result['ota_msg']
        })

    @gen.coroutine
    def get_ota(self, thing_key):
        try:
            result = yield self.api('/v1/ota/status', query={"access_token": thing_key}, method="GET")
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
