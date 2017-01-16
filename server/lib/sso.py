#!/usr/bin/env python
# coding=utf-8
import time
import jwt
import json
import re
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from tornado import gen
from tornado.httpclient import AsyncHTTPClient


class Sso(object):
    @gen.coroutine
    def auth_token(self, token):
        """Return {'user_id': '', 'token': '', 'expire': "1470738102"},
        if token have not expire, set expire to 0,
        if authentication fail, return None
        """
        raise NotImplementedError("Please Implement this method")
        

class FirebaseSso(Sso):
    """Example Firebase Authentication, Locally verify.
    More info:
    https://firebase.google.com/docs/auth/
    https://firebase.google.com/docs/auth/server/verify-id-tokens#verify_id_tokens_using_a_third-party_jwt_library
    """
    PROJECT_ID = 'wioapp-c70a8'
    CERT_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'
    
    public_cert = {}
    cert_expire = 0
    
    @gen.coroutine
    def auth_token(self, token):
        """Get user info form firebase

        example:
        {
            'picture': 'https://scontent.xx.fbcdn.net/XXX.jpg',
            'sub': 'OCbl1hXpURcGp1s8MvyDxA27PXXX',
            'user_id': 'OCbl1hXpURcGp1s8MvyDxA27PXXX',
            'name': 'XX Ten',
            'iss': 'https://securetoken.google.com/wioapp-c70a8',
            'email_verified': False, 'firebase': {
                'sign_in_provider': 'facebook.com',
                'identities': {
                    'facebook.com': ['XXX'],
                    'email': ['XXX@hotmail.com']
                }
            },
            'exp': 1484559214,
            'auth_time': 1480328550,
            'iat': 1484555614,
            'email': 'XXX@hotmail.com',
            'aud': 'wioapp-c70a8'
        }
        """
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        if not kid:
            raise Exception("The JWT token not include KID")
        
        if int(time.time()) >= self.cert_expire:
            try:
                yield self.request_cert()
            except Exception as e:
                raise Exception("Requires JWT public certificate failure, {}".format(str(e)))

        if self.public_cert.get(kid) is None:
            raise Exception("Authentication(kid) has expired")

        try:
            cert_obj = load_pem_x509_certificate(self.public_cert.get(kid).encode('utf-8'), default_backend())
            public_key = cert_obj.public_key()
            payload = jwt.decode(token, public_key, audience=self.PROJECT_ID, algorithms=['RS256'], verify=True)
        except Exception as e:
            raise Exception("Verify JWT token failure, {}".format(str(e)))

        raise gen.Return({'user_id': payload['user_id'], 'token': token, 'expire': payload['exp'], "ext": payload})
        
    @gen.coroutine
    def request_cert(self):
        http_client = AsyncHTTPClient()
        try:
            res = yield http_client.fetch(self.CERT_URL)
            self.public_cert = json.loads(res.body)
            cc = res.headers['Cache-Control']
            max_age = re.search("max-age=([0-9]+)", cc).groups()[0]
            self.cert_expire = int(time.time()) + int(max_age)
        except:
            raise

        
sso = FirebaseSso()
