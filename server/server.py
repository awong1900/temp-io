#!/usr/bin/env python
# coding=utf-8
import tornado.ioloop
import tornado.web
from tornado.log import gen_log
from tornado.options import define
from tornado.options import options
from handler import UserHandler
from handler import UserIdHandler
from handler import TempHandler
from handler import TempIdHandler
from handler import TempVerifyActivationHandler
from handler import TempTemperaturesHandler
from handler import TempOtaHandler
from handler import TempsHandler
from handler import BoardsHandler
import db
from lib.temp_task import TempTask

define("port", type=int, default=8888, help="Run server on a specific port")
define("debug", type=int, default=1, help="0:false, 1:true")
temp_task = TempTask()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    setting = dict(
        debug=True if options.debug else False,
        login_url='/',
        temp_task=temp_task
    )
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/v1/users/(.+)/temps/*", TempHandler),
        (r"/v1/users/(.+)/temps/(.+)/verify-activation/*", TempVerifyActivationHandler),
        (r"/v1/users/(.+)/temps/(.+)/temperatures/*", TempTemperaturesHandler),
        (r"/v1/users/(.+)/temps/(.+)/ota/*", TempOtaHandler),
        (r"/v1/users/(.+)/temps/(.+)/*", TempIdHandler),
        (r"/v1/me/*", UserHandler),
        (r"/v1/users/(.+)/*", UserIdHandler),
        (r"/v1/temps", TempsHandler),
        (r"/v1/boards", BoardsHandler),
    ], **setting)

if __name__ == "__main__":
    from tornado.log import enable_pretty_logging
    enable_pretty_logging()
    options.parse_command_line()
    gen_log.info(db.uri)
    gen_log.info("http://localhost:{}".format(options.port))
    app = make_app()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().add_callback(temp_task.start_task_once)
    tornado.ioloop.IOLoop.current().start()
