#!/usr/bin/env python
# coding=utf-8
import uuid
from tornado import gen

class Wio(object):
    """docstring for Wio.
    
        Ansy http access from wio server.
    """
    def __init__(self):
        super(Wio, self).__init__()
    
    @gen.coroutine
    def add_thing(self):
        gen.Return({
            "id": uuid.uuid4().hex,
            "key": uuid.uuid4().hex,
            "online": False
        })

    @gen.coroutine
    def get_thing(self, id):
        gen.Return({
            "id": id,
            "key": '123',
            "online": False
        })

    @gen.coroutine
    def get_temp(self, id):
        gen.Return({
            "temp": "15"
        })

wio = Wio()
