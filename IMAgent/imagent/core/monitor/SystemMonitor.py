# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2013-12-06
@contact: jhx1008@gmail.com
version:  1.0
@todo:    系统资源监控，监控磁盘IO，内存使用, 系统活动情况等
@modify:
"""

import subprocess

from imagent.core.common.Util import Util
from imagent.core.monitor.Monitor import Monitor


class SystemMonitor(Monitor):
    def __init__(self, context, threadName="SystemMonitor"):

        interval = context.userConfig.get_monitors_interval()
        Monitor.__init__(self, context=context, alias='os',threadName=threadName,
                         activeReportInterval=interval['activeInterval'],
                         interval=interval['systemInterval']
                         )

        self.msgInfo = {}
        self.dfMsg = []

    def doWork(self):
        # sar -d获取磁盘统计信息，-p显示磁盘名称
        # sar -r获取内存统计信息
        # sar -u获取cpu统计信息
        # sar -n DEV获取网卡流量信息
        cmd = "sar -d -r -p -u -n DEV 1 1 | grep -E 'Average|平均时间'"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        p.wait()
        lines = p.stdout.readlines()
        currentType = ''
        tempDict = {}
        for line in lines:
            line = line.split(':')[1].strip()
            if line.find('CPU') != -1:
                currentType = 'cpu'
                tempDict[currentType] = [line, ]
                continue
            elif line.find('memfree') != -1:
                currentType = 'memory'
                tempDict[currentType] = [line, ]
                continue
            elif line.find('DEV') != -1:
                currentType = 'disk'
                tempDict[currentType] = [line, ]
                continue
            elif line.find('IFACE') != -1:
                currentType = 'network'
                tempDict[currentType] = [line, ]
                continue
            tempDict[currentType].append(line)

        cmd = "df | awk -F ' ' '{if(NR != 1)print $1,$5}'"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        p.wait()
        lines = p.stdout.readlines()

        self.lock.acquire()
        self.msgInfo = tempDict
        self.dfMsg = lines
        self.lock.release()

    def getInfos(self):
        self.lock.acquire()
        msgInfo = Util.deepCopy(self.msgInfo)
        self.lock.release()
        keys = msgInfo.keys()
        ret = {}
        for key in keys:
            infoList = msgInfo[key]
            head = infoList[0].split()
            infoList = infoList[1:]
            tempList = []
            for info in infoList:
                temp = info.split()
                if key == 'cpu':
                    for i in xrange(1, len(temp)):
                        tempList.append({head[i]: temp[i]})
                elif key == 'memory':
                    for i in xrange(len(temp)):
                        tempList.append({head[i]: temp[i]})
                # DEV or IFACE
                else:
                    l = []
                    for i in xrange(1, len(temp)):
                        l.append({head[i]: temp[i]})
                    d = {temp[0]: l}
                    tempList.append(d)
            ret[key] = tempList
        return ret

    def getInfos2(self):
        self.lock.acquire()
        msgInfo = Util.deepCopy(self.msgInfo)
        dfMsg = Util.deepCopy(self.dfMsg)
        self.lock.release()
        keys = msgInfo.keys()
        ret = {}
        for key in keys:
            infoList = msgInfo[key]
            head = infoList[0].split()
            infoList = infoList[1:]
            tempDir = {}
            for info in infoList:
                temp = info.split()
                if key == 'cpu':
                    for i in xrange(1, len(temp)):
                        tempDir[head[i]] = temp[i]
                elif key == 'memory':
                    for i in xrange(len(temp)):
                        tempDir[head[i]] = temp[i]
                # DEV or IFACE
                else:
                    d = {}
                    for i in xrange(1, len(temp)):
                        d[head[i]] = temp[i]
                    if key == 'disk':
                        tps = float(d['tps'])
                        wsec = float(d['wr_sec/s'])
                        rsec = float(d['rd_sec/s'])
                        if tps == 0:
                            d['wtps'] = '0.00'
                            d['rtps'] = '0.00'
                        else:
                            #处理除零错误
                            if wsec + rsec == 0:
                                wtps = 0
                                rtps = 0
                            else:
                                wtps = tps * wsec / (wsec + rsec)
                                rtps = tps - wtps
                            d['wtps'] = "%.02f" % wtps
                            d['rtps'] = "%.02f" % rtps

                    tempDir[temp[0]] = d
            ret[key] = tempDir
        if ret.has_key('disk'):
            partition_used = {}
            for line in dfMsg:
                key, value = line.split()
                partition_used[key] = value[:-1]
            ret['disk']['partition'] = partition_used
        return ret

    def getData(self):
        systemInfo = self.getInfos2()
        if len(systemInfo) == 0:
            return None
        netValue = systemInfo.pop('network')
        return {self.alias:systemInfo,'network':netValue}