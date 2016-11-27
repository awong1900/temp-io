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
        # db = self.settings['db']
        pass
        
    @gen.coroutine
    def prepare(self):
        self.user, self._message = yield self.get_user(self.get_access_token())
        
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
                print 22, result
                user = doc_user
            except Exception as e:
                gen_log.error(e)
                raise gen.Return((None, "SSO authenticate token failure, {}".format(str(e))))
        else:
            print 111
            pass  # return user
        # if t:
        #     if t.expire != datetime.utcfromtimestamp(0) and t.expire < datetime.utcnow():
        #         raise gen.Return((None, "Authentication has expired"))
        #     u = self.user_schema.get_user_by_uid(t.user_id)
        #     if not u:
        #         raise gen.Return((None, "User has deleted"))
        #     user = u.as_dict()
        # else:
        #     try:
        #         data = yield sso.auth_token(token)
        #         u = self.user_schema.add_user(data['user_id'])
        #         self.user_token_schema.add_user_token(data['user_id'],
        #             data['token'], datetime.utcfromtimestamp(int(data['expire'])))
        #         self.user_token_schema.del_exp_user_token(data['user_id'])
        #         user = u.as_dict()
        #     except Exception as e:
        #         gen_log.error(e)
        #         raise gen.Return((None, "SSO authenticate token failure, {}".format(str(e))))
            
        # user['is_admin'] = True if config.admins.get(user['user_id']) else False
        # user['token'] = token
        raise gen.Return((user, ''))

    @property
    def db_user(self):
        return User()
        
    @property
    def db_temp(self, arg):
        return Temp()
