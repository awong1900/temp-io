#!/usr/bin/env python
# coding=utf-8
from tornado import gen
from tornado.web import authenticated
from base import BaseHandler
from base import UserBaseHandler
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


class UserIdHandler(UserBaseHandler):
    """read user info with specify user id."""
    @gen.coroutine
    def get(self, uid):
        if self.user and self.user['myself']:
            self.req_user.pop('tokens')
            self.finish(jsonify(self.req_user))
        else:
            self.req_user.pop('tokens')
            self.req_user.pop('email')
            self.req_user.pop('sign_in_provider')
            self.finish(jsonify(self.req_user))
