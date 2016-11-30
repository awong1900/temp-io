#!/usr/bin/env python
# coding=utf-8

import tornado.ioloop
import tornado.web
from tornado.log import gen_log
from handler import UserHandler
from handler import UserIdHandler
from handler import TempHandler
from handler import TempIdHandler
from handler import TempsHandler
import db


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    setting = dict(
        debug=True,
        login_url='/'
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
    from tornado.log import enable_pretty_logging
    enable_pretty_logging()
    gen_log.info(db.uri)
    gen_log.info("http://localhost:8888")
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
