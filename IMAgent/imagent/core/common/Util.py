# -*- coding:UTF-8 -*- 
"""
@author:  jianghongxiang
@date:    2014-12-25
@contact: jhx1008@gmail.com
version:  1.0
@todo:    公共类，用于定义一些公共方法
@modify:
"""
import os
import time
import json
import copy
import datetime

from imagent.core.common.AgentException import AgentException


class CJsonEncoder(json.JSONEncoder):
    """
    原来的json不支持datetime
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

#单例模式装饰器
def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


class Util:
    @staticmethod
    def getRealPath(path):
        """
         获取给定路径的绝对路径
        """
        return os.path.realpath(path)

    @staticmethod
    def pathSplit(fileName):
        """
         给定文件路径，返回文件的路径和文件名
        """
        return os.path.split(fileName)

    @staticmethod
    def isExists(path):
        """
        """
        return os.path.exists(path)

    @staticmethod
    def getFileSize(path):
        """
        """
        return os.path.getsize(path)

    @staticmethod
    def popen(cmd):
        """
        """
        return os.popen(cmd)

    @staticmethod
    def sleep(seconds):
        """
        """
        return time.sleep(seconds)

    @staticmethod
    def msleep(micro_seconds):
        """
        """
        return time.sleep(float(micro_seconds) / 1000)

    @staticmethod
    def getTimeLong():
        return long(time.time())

    @staticmethod
    def getTimeStr():
        return time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def json2Obj(msg):
        """
        """
        obj = None
        try:
            obj = json.loads(msg)
        except ValueError:
            raise AgentException("load string to dic error, {0} not a json format".format(msg))
        except Exception, e:
            raise AgentException("unknown error: {0}".format(e))
        return obj

    @staticmethod
    def obj2Json(obj):
        """
        """
        return json.dumps(obj, cls=CJsonEncoder)

    @staticmethod
    def deepCopy(obj):
        """
        """
        return copy.deepcopy(obj)
