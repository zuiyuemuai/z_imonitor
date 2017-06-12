#coding=utf-8
import json

from imagent.core.monitor.Monitor import Monitor


class StatusMonitor(Monitor):
    def __init__(self, context, threadName="StatusMonitor"):
        interval = context.userConfig.get_monitors_interval()
        Monitor.__init__(self, context=context,alias='mongo', threadName=threadName,
                         activeReportInterval=interval['activeInterval'],
                         interval=0
                         )
        self.interval = int(interval['statusmonitor'])
        self.dataBaseInstance = context.dataBaseInstance

    def doWork(self):
        try:
            items = ['command','getmore', 'conn','update','delete','insert','query','res','vsize','netIn','netOut']
            temp = {}
            for item in items:
                temp[item] = 0
            data = self.dataBaseInstance.getMongoStat(self.interval)
            for line in data:
                jdata = json.loads(line)
                for name,rowData in jdata.iteritems():
                    if len(rowData['command'].split('|')) == 2:
                        temp['command'] += int(rowData['command'].split('|')[0])
                    else:
                        temp['command'] += int(rowData['command'])
                    temp['getmore'] += int(rowData['getmore'])
                    temp['conn'] += int(rowData['conn'])

                    temp['update'] += self.getInt(rowData['update'])
                    temp['delete'] += self.getInt(rowData['delete'])
                    temp['insert'] += self.getInt(rowData['insert'])
                    temp['query'] += self.getInt(rowData['query'])

                    temp['res'] += float(rowData['res'][:-1])*1024*1024
                    temp['vsize'] += float(rowData['vsize'][:-1])*1024*1024

                    temp['netIn'] += self.changeUnit(rowData['netIn'])
                    temp['netOut'] += self.changeUnit(rowData['netOut'])

            for item in items:
                temp[item] = temp[item]/self.interval
            self.lock.acquire()
            self.dataDict = temp
            self.lock.release()
        except Exception, e:
            # print e
            raise e
    '''
    获取值，因为statu出来的数据零是以*0表示的
    '''
    def getInt(self, str):
        try:
            return int(str)
        except ValueError:
            return 0

    def changeUnit(self, str):
        if str[-1:] == 'b':
            return float(str[:-1])
        elif str[-1:] == 'k':
            return float(str[:-1])*1024
        elif str[-1:] == 'm' or str[-1:] == 'M':
            return float(str[:-1])*1024*1024
        elif str[-1:] == 'g' or str[-1:] == 'G':
            return float(str[:-1])*1024*1024*1024
        return float(str[:-1])