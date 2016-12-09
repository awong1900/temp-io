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
import config


class TempTask(object):
    """Regularly read temperature data through the WIO IOT server
    """
    TEMP_URL = "{}/v1/node/GroveTempHumD0/temperature".format(config.wio['base_url'])
    SLEEP_URL = "{}/v1/node/pm/sleep".format(config.wio['base_url'])
    tasks = set()

    def is_in_tasks(self, temp_id):
        return True if temp_id in self.tasks else False

    def add_in_tasks(self, temp_id):
        if self.is_in_tasks(temp_id) is False:
            IOLoop.current().add_callback(self.task, temp_id)
            self.tasks.add(temp_id)

    @gen.coroutine
    def remove_from_tasks(self, temp_id, status=None, status_text=None):
        self.tasks.remove(temp_id)
        if status is None:
            yield Temp().update_temp(temp_id, {"status": status, "status_text": status_text})

    @staticmethod
    @gen.coroutine
    def update_status(temp_id, status, status_text):
        yield Temp().update_temp(temp_id, {"status": status, "status_text": status_text})

    @staticmethod
    @gen.coroutine
    def close_temp(temp_id):
        yield Temp().update_temp(temp_id, {"open": False})

    @staticmethod
    @gen.coroutine
    def update_temp(temp_id, temp):
        yield Temp().update_temp(
            temp_id,
            {"temperature": temp, "temperature_at": datetime.utcnow()},
            {"value": temp, "created_at": datetime.utcnow()})

    @gen.coroutine
    def task(self, *args):
        temp_id = args[0]
        http_client = AsyncHTTPClient()
        gen_log.info("=== Do task id({})====".format(temp_id))

        doc = yield Temp().get_temp(temp_id)
        if doc is None:
            gen_log.info("Temp({}) be deleted!".format(temp_id))
            yield self.remove_from_tasks(temp_id)
            raise gen.Return()

        access_token = doc.get('key')
        period = doc.get('read_period')
        temp_open = doc.get('open')
        has_sleep = doc.get('has_sleep')

        if not temp_open:
            gen_log.info("Temp({}) be closed!".format(temp_id))
            yield self.remove_from_tasks(temp_id, "normal", "The temp is closed.")
            raise gen.Return()

        end_time = time.time()+(3*period)
        while True:
            try:
                temps = []
                for i in range(4):
                    res = yield http_client.fetch(
                        "{}?access_token={}".format(self.TEMP_URL, access_token),
                        request_timeout=10)
                    temps.append(json.loads(res.body)['celsius_degree'])
                    yield gen.sleep(2)

                temp = round(sum(temps[1:])/(len(temps)-1), 1)
            except Exception as e:
                if time.time() > end_time:
                    gen_log.error(e)
                    yield self.remove_from_tasks(temp_id, "error", "The node is not wake up on three period.")
                    self.close_temp(temp_id)
                yield gen.sleep(5)
                gen_log.info(e)
                continue

            gen_log.info("{} ==> {}".format(temps, temp))
            self.update_temp(temp_id, temp)
            break

        if has_sleep is True:
            try:
                yield http_client.fetch(
                    "{}/{}?access_token={}".format(self.SLEEP_URL, period-10, access_token),
                    method='POST',
                    body=urllib.urlencode({}))
                self.update_status(temp_id, "normal", "The node is sleep mode.")
            except Exception as e:
                gen_log.error(e)
        else:
            self.update_status(temp_id, "normal", "The node is online mode.")

        IOLoop.current().add_timeout(time.time()+(period or 60), self.task, temp_id)
        print self.tasks
        gen_log.info("===End task and restart({})====".format(temp_id))
