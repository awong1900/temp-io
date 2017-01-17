#!/usr/bin/env python
# coding=utf-8
import time
from datetime import datetime
from tornado import gen
from tornado.log import gen_log
from tornado.ioloop import IOLoop
from db import Temp
from db import Temperature
from lib.wio import Wio
from utils import fahrenheit


class TempTask(object):
    """Regularly read temperature data through the WIO IOT server"""
    tasks = set()

    def is_in_tasks(self, temp_id):
        return True if temp_id in self.tasks else False

    def add_in_tasks(self, temp_id):
        if self.is_in_tasks(temp_id) is False:
            self.tasks.add(temp_id)
            IOLoop.current().add_callback(self.task, temp_id)

    @gen.coroutine
    def remove_from_tasks(self, temp_id, status=None, status_text=None):
        gen_log.info("===> remove Temp({}) from tasks".format(temp_id))
        self.tasks.remove(temp_id)
        if status is not None:
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
        yield Temp().update_temp(temp_id, {"temperature": temp,
                                           "temperature_f": fahrenheit(temp),
                                           "temperature_updated_at": datetime.utcnow()})
        yield Temperature().update_temperature(temp_id, {"temperature": temp,
                                                         "temperature_f": fahrenheit(temp),
                                                         "created_at": datetime.utcnow()})

    @gen.coroutine
    def task(self, *args):
        temp_id = args[0]
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
        board_type_id = doc.get('board_type_id')

        if not temp_open:
            gen_log.info("Temp({}) be closed!".format(temp_id))
            yield self.remove_from_tasks(temp_id, "normal", "The temp is closed.")
            raise gen.Return()

        end_time = time.time()+(3*period)
        while True:
            try:
                temps = []
                wio = Wio(access_token)
                for i in range(4):
                    result = yield wio.get_temp(board_type_id)
                    temps.append(result)
                    yield gen.sleep(1)

                temp = round(sum(temps[1:])/(len(temps)-1), 1)
            except Exception as e:
                # TODO, if not pulgin grove temp, will gen error
                if time.time() > end_time:
                    gen_log.error("Temp({}) {}".format(temp_id, e))
                    yield self.remove_from_tasks(temp_id, "error", "The node is not wake up on three period.")
                    yield self.close_temp(temp_id)
                    raise gen.Return()
                yield gen.sleep(5)
                gen_log.info("Temp({}) {}".format(temp_id, e))
                continue

            gen_log.info("{} ==> {}".format(temps, temp))
            self.update_temp(temp_id, temp)
            break

        if has_sleep is True:
            wio = Wio(access_token)
            try:
                yield wio.sleep(period, board_type_id)
                self.update_status(temp_id, "normal", "The node is sleep mode.")
            except Exception as e:
                gen_log.error(e)
        else:
            self.update_status(temp_id, "normal", "The node is online mode.")

        IOLoop.current().add_timeout(time.time()+(period or 60), self.task, temp_id)
        gen_log.info("task ids: ({})".format(self.tasks))
        gen_log.info("===End task and restart({})====".format(temp_id))

    @gen.coroutine
    def start_task_once(self):
        cursor = Temp().get_all_open_temp()
        while (yield cursor.fetch_next):
            temp = cursor.next_object()
            self.add_in_tasks(temp['id'])
