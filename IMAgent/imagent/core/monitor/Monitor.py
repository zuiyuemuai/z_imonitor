#coding=utf-8
import threading

from imagent.core.common.BaseThread import BaseThread
from imagent.core.common.Util import Util


class Monitor(BaseThread):
    #alias为别名，用于上传数据时使用的名称，如os，topsql等简短的名称
    def __init__(self,context, alias='alias', threadName="Monitor", activeReportInterval=5.0, interval=1):
        BaseThread.__init__(self, threadName, activeReportInterval, interval)
        self.alias = alias
        self.context = context
        self.lock = threading.Lock()
        self.dataDict = {}

    def doWork(self):
        pass

    def getData(self):
        self.lock.acquire()
        ret = Util.deepCopy(self.dataDict)
        self.lock.release()
        return {self.alias:ret}

class MonitorWithSender(Monitor):
    def __init__(self,context, sender, alias='alias', threadName="Monitor", activeReportInterval=5.0, interval=1):
        Monitor.__init__(self, context, alias, threadName,activeReportInterval, interval)
        self.sender = sender
