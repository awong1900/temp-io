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
tasks = set()

@gen.coroutine
def task(*args):
    gen_log.info("=== task({})====".format(args[0]))
    temp_id = args[0]
    tasks.add(temp_id)
    
    doc = yield Temp().get_temp(temp_id)
    if doc is None:
        gen_log.info("Temp({}) be deleted!".format(args[0]))
        raise gen.Return()
    access_token = doc.get('key')
    period = doc.get('read_period')
    is_open = doc.get('open')
    has_sleep = doc.get('has_sleep')
    
    if not is_open:
        gen_log.info("Temp({}) be closed!".format(args[0]))
        yield Temp().update_temp(temp_id,
            {"status": "normal", "status_text": "The temp is closed."})
        raise gen.Return()
        
    http_client = AsyncHTTPClient()
    first_time = time.time()
    end_time = first_time + (3 * period)
    while True:
        try:
            res = yield http_client.fetch(test_url, request_timeout=10)
            temp = json.loads(res.body)['celsius_degree']
        except Exception as e:
            if (time.time() > end_time):
                gen_log.error(e)
                yield Temp().update_temp(temp_id,
                    {"status": "error", "status_text": "The node is not wake up on three period.", "open": False})
                raise gen.Return()
            yield gen.sleep(5)
            gen_log.info(e)
            continue
            
        yield Temp().update_temp(temp_id,
            {"temperature": temp, "temperature_at": datetime.utcnow()})
        print temp
        break
    print access_token, period
    
    if has_sleep is True:
        try:
            body = urllib.urlencode({})
            res = yield http_client.fetch("{}/{}?access_token={}".format(sleep_url, period-10, token), method='POST', body=body)
            yield Temp().update_temp(temp_id,
                {"status": "normal", "status_text": "The node is on sleep mode."})
            print res.body
        except Exception as e:
            gen_log.error(e)
            # raise gen.Return()
            
    IOLoop.current().add_timeout(time.time() + (period or 5), task, temp_id)
    print tasks
    gen_log.info("===End task and restart({})====".format(args[0]))

def is_task_queue(temp_id):
    return True if temp_id in tasks else False
