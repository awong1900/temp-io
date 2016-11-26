#!/usr/bin/env python
# coding=utf-8

import tornado.ioloop
import tornado.web
from handler import UserHandler
from handler import UserIdHandler
from handler import TempHandler
from handler import TempIdHandler
from handler import TempsHandler

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    setting = dict(
        debug=True,
    )
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/user/*", UserHandler),
        (r"/users/(.+)/*", UserIdHandler),
        (r"/users/(.+)/temps/*", TempHandler),
        (r"/users/(.+)/temps/(.+)/*", TempIdHandler),
        (r"/temps", TempsHandler),
    ], **setting)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
