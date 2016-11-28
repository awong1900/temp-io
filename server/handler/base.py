#!/usr/bin/env python
# coding=utf-8
from datetime import datetime
from tornado import gen
from tornado.web import RequestHandler
from tornado.log import gen_log
from lib import sso
from db import User
from db import Temp

class BaseHandler(RequestHandler):
    """docstring for BaseHandler."""
    def initialize(self):
        pass
        
    @gen.coroutine
    def prepare(self):
        self.user, self._message = yield self.get_user(self.get_access_token())
        print self.user
        
    def get_access_token(self):
        token = self.get_argument("access_token", "")
        if not token:
            try:
                token_str = self.request.headers.get("Authorization")
                token = token_str.replace("token ", "")
            except:
                token = ""
        gen_log.debug('token: "{}"'.format(token))
        return token

    @gen.coroutine
    def get_user(self, token):
        if not token:
            raise gen.Return((None, "Requires authentication"))
            
        user = None
        result = yield self.db_user.get_user_by_token(token)
        if result is None:
            try:
                data = yield sso.auth_token(token)
                doc_user = {
                    'id': data['user_id'],
                    'tokens': [
                        {
                            'token': data['token'],
                            'expire': datetime.utcfromtimestamp(int(data['expire']))
                        }
                    ]}
                result = yield self.db_user.add_user(data['user_id'], doc_user)
                user = {'id': data['user_id']}
            except Exception as e:
                gen_log.error(e)
                raise gen.Return((None, "SSO authenticate token failure, {}".format(str(e))))
        else:
            result = yield self.db_user.is_expire(token)
            if result is None:
                raise gen.Return((None, "Authentication has expired"))
            user = {'id': result['id']}

        raise gen.Return((user, ''))

    @property
    def db_user(self):
        return User()
        
    @property
    def db_temp(self, arg):
        return Temp()