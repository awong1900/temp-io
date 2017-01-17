#!/usr/bin/env python
# coding=utf-8
from datetime import datetime
from tornado_cors import CorsMixin
from tornado import gen
from tornado.web import RequestHandler
from tornado.web import HTTPError
from tornado.log import gen_log
import config
from lib import sso
from db import User
from db import Temp
from db import Temperature


class BaseHandler(CorsMixin, RequestHandler):
    """docstring for BaseHandler."""
    CORS_ORIGIN = '*'
    CORS_HEADERS = 'Content-Type, Authorization'

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.req_token = None
        self.temp_task = self.settings['temp_task']
        self.user = None
        self.req_user = None
        self._message = None

    @gen.coroutine
    def prepare(self):
        self.req_token = self.get_access_token()
        self.req_user, self._message = yield self.get_user(self.req_token)
        if self.req_user:
            self.req_user['is_admin'] = True if config.admins.get(self.req_user['id']) else False
        self.user = self.req_user

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
            
        user = yield self.db_user.get_user_by_token(token)
        if user is None:
            try:
                data = yield sso.auth_token(token)
                doc_user = {
                    'id': data['user_id'],
                    'name': data['ext']['name'],
                    'sign_in_provider': data['ext']['firebase']['sign_in_provider'],
                    'email': '' or data['ext'].get('email'),
                    'picture': '' or data['ext'].get('picture'),
                    'pro': False,
                    'tokens': [
                        {
                            'token': data['token'],
                            'expire': datetime.utcfromtimestamp(int(data['expire']))
                        }
                    ]}
                yield self.db_user.add_user(data['user_id'], doc_user)
                raise gen.Return((doc_user, ''))
            except Exception as e:
                gen_log.error(e)
                raise HTTPError(400, "SSO authenticate token failure, {}".format(str(e)))
        else:
            result = yield self.db_user.is_expire(token)
            if result is None:
                raise HTTPError(400, "Authentication has expired")
            raise gen.Return((user, ''))

    def get_current_user(self):
        if self.req_user is None:
            raise HTTPError(400, "{}".format(self._message))
        else:
            return self.req_user

    def write_error(self, status_code, **kwargs):
        message = kwargs['exc_info'][1].log_message
        self.finish({"error": message})

    @property
    def db_user(self):
        return User()
        
    @property
    def db_temp(self):
        return Temp()

    @property
    def db_temperature(self):
        return Temperature()


class UserBaseHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super(UserBaseHandler, self).__init__(application, request, **kwargs)
        self.target_user = None

    @gen.coroutine
    def prepare(self):
        yield super(UserBaseHandler, self).prepare()
        uid = self.path_args[0]
        if self.req_user:
            self.req_user['myself'] = True if uid == self.req_user['id'] else False

        if self.req_user and self.req_user['myself'] is True:
            self.target_user = self.req_user
        else:
            self.target_user = yield self.db_user.get_user_by_uid(uid)
            if self.target_user is None:
                raise HTTPError(404, "User not found!")


class TempBaseHandler(UserBaseHandler):
    def __init__(self, application, request, **kwargs):
        super(TempBaseHandler, self).__init__(application, request, **kwargs)
        self.temp = None

    @gen.coroutine
    def prepare(self):
        yield super(TempBaseHandler, self).prepare()
        tid = self.path_args[1]
        self.temp = yield self.db_temp.get_temp(tid)
        if self.temp is None:
            raise HTTPError(404, "Temp-io not found!")
