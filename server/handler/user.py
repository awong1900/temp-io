#!/usr/bin/env python
# coding=utf-8
import json
from tornado import gen
from tornado.web import authenticated
from base import BaseHandler


class UserHandler(BaseHandler):
    """docstring for UserHandler."""
    @gen.coroutine
    @authenticated
    def get(self):
        uid = self.current_user['id']
        user = yield self.db_user.get_user_by_uid(uid)
        user.pop('_id')
        user.pop('tokens')
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(user))


class UserIdHandler(BaseHandler):
    """docstring for UserIdHandler."""
    def get(self):
        pass
