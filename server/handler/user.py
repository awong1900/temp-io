#!/usr/bin/env python
# coding=utf-8
import json
from tornado import gen
from tornado.web import authenticated
from base import BaseHandler
from lib.utils import jsonify


class UserHandler(BaseHandler):
    """docstring for UserHandler."""
    @gen.coroutine
    @authenticated
    def get(self):
        uid = self.current_user['id']
        user = yield self.db_user.get_user_by_uid(uid)
        user.pop('tokens')
        self.finish(jsonify(user))


class UserIdHandler(BaseHandler):
    """docstring for UserIdHandler."""
    @gen.coroutine
    # @authenticated
    def get(self, uid):
        print 1111
        user = yield self.db_user.get_user_by_uid(uid)
        user.pop('tokens')
        self.finish(jsonify(user))
