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
            self.target_user.pop('tokens')
            self.finish(jsonify(self.target_user))
        else:
            self.target_user.pop('tokens')
            self.target_user.pop('email')
            self.target_user.pop('sign_in_provider')
            self.finish(jsonify(self.target_user))
