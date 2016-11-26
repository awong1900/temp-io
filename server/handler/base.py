#!/usr/bin/env python
# coding=utf-8
from tornado import gen
from tornado.web import RequestHandler
from tornado.log import gen_log
from lib import sso


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
            
        data = yield sso.auth_token(token)
        raise gen.Return(('', ''))
        # t = self.user_token_schema.get_user_token_by_token(token)
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
        # raise gen.Return((user, ''))
