# -*- coding:UTF-8 -*-

from imagent.core.monitor.Monitor import Monitor

class SlaveStatusMonitor(Monitor):
    def __init__(self, context, threadName="SlaveStatusMonitor" ):

        interval = context.userConfig.get_monitors_interval()
        Monitor.__init__(self, context=context,alias='slave', threadName=threadName,
                         activeReportInterval=interval['activeInterval'],
                         interval=interval['statusInterval']
                         )
        averageSlave = context.userConfig.get_monitors_attr('SlaveStatusMonitor'.lower())['average']
        self.dataBaseInstance = context.dataBaseInstance
        self.averageDict = {}
        for elem in averageSlave.split(";"):
            self.averageDict[elem] = None

    def doWork(self):
        rows = self.dataBaseInstance.getSlaveStatus()
        if rows != None:
            temp = {}
            for (key, value) in rows:
                prev = self.averageDict.get(key, 'INVALID')
                if prev == 'INVALID':
                    temp[key] = value
                else:
                    self.averageDict[key] = long(value)
                    # 如果保存的前值为None，说明Agent刚启动，第一条数据不推送
                    if prev == None:
                        continue
                    cValue = long(value)
                    # 如果是MySQL重启了，status值被清空了，新取到的值会小于历史值，这种情况下，直接返回0
                    if cValue < prev:
                        cValue = prev
                    tmpValue = float(cValue - prev) / self.loopInterval
                    temp[key] = "%.2f" % tmpValue
            self.lock.acquire()
            self.dataDict = temp
            self.lock.release()


