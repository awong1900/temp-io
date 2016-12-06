#!/usr/bin/env python
# coding=utf-8
import time
import urllib
from datetime import datetime
import json
from tornado import gen
from tornado.log import gen_log
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient
from db import Temp

token = '88f9727e6284476b6de1122cf9c0d1d7'
test_url = 'https://us.wio.seeed.io/v1/node/GroveTempHumD0/temperature?access_token={}'.format(token)
sleep_url = 'https://us.wio.seeed.io/v1/node/pm/sleep'
# [sleep_time_sec]?

@gen.coroutine
def task(*args):
    gen_log.info("=== task({})====".format(args[0]))
    temp_id = args[0]
    
    doc = yield Temp().get_temp(temp_id)
    if doc is None:
        gen_log.info("Temp({}) be deleted!".format(args[0]))
        raise gen.Return()
    access_token = doc.get('key')
    # gen.sleep(2)  # request temp
    http_client = AsyncHTTPClient()
    try:
        res = yield http_client.fetch(test_url)
        temp = json.loads(res.body)['celsius_degree']
        yield Temp().update_temp(temp_id,
            {"temperature": temp, "temperature_at": datetime.utcnow()})
    except Exception as e:
        raise
        
    period = doc.get('read_period')
    print access_token, period
    try:
        body = urllib.urlencode({})
        res = yield http_client.fetch("{}/{}?access_token={}".format(sleep_url, period-10, token), method='POST', body=body)
        print res.body
    except:
        raise
        
    IOLoop.current().add_timeout(time.time() + (period or 5), task, temp_id)
    gen_log.info("===End task and restart({})====".format(args[0]))
