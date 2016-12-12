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
    def get_thing(self, tid):
        raise gen.Return({
            "id": id,
            "key": '123',
            "online": False
        })

    @gen.coroutine
    def get_temp(self, id):
        raise gen.Return({
            "temp": "15"
        })

    @gen.coroutine
    def get_node_list(self):
        pass
