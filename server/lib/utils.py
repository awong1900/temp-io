#!/usr/bin/env python
# coding=utf-8
import json
from datetime import datetime
from bson.objectid import ObjectId
import os


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(obj, ObjectId):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


def jsonify(result):
    return json.loads(json.dumps(result, cls=JSONEncoder))


def fahrenheit(x):
    return x * 1.8 + 32


def get_base_dir():
    path = os.path.dirname(os.path.realpath(__file__))
    return os.path.abspath(path + "/..")
