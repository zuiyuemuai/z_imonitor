# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-03
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""
from imagent.core.monitor.Monitor import Monitor
from imagent.core.common.AgentLog import AgentLog

class TopSQLMonitor(Monitor):
    """
    对于TopSQL的监控
    """
    def __init__(self, context, threadName="TopSQLMonitor"):
        interval = context.userConfig.get_monitors_interval()
        Monitor.__init__(self, context=context,alias='topsql', threadName=threadName,
                         activeReportInterval=interval['activeInterval'],
                         interval=interval['topsqlInterval']
                         )
        self.topNum = context.userConfig.get_monitors_attr('TopSQLMonitor'.lower())['topn']
        self.fields = context.userConfig.get_monitors_attr('TopSQLMonitor'.lower())['fields'].split(';')

        self.dataBaseInstance = context.dataBaseInstance

    def doWork(self):
        try:
            temp = {}
            items = ['COUNT_STAR', 'SUM_TIMER_WAIT',
                           'MIN_TIMER_WAIT', 'AVG_TIMER_WAIT', 'MAX_TIMER_WAIT', 'SUM_LOCK_TIME',
                           'SUM_ERRORS', 'SUM_WARNINGS', 'SUM_ROWS_AFFECTED',
                           'SUM_ROWS_SENT', 'SUM_ROWS_EXAMINED', 'SUM_CREATED_TMP_DISK_TABLES',
                           'SUM_CREATED_TMP_TABLES', 'SUM_SELECT_FULL_JOIN',
                           'SUM_SELECT_FULL_RANGE_JOIN', 'SUM_SELECT_RANGE',
                           'SUM_SELECT_RANGE_CHECK', 'SUM_SELECT_SCAN', 'SUM_SORT_MERGE_PASSES',
                           'SUM_SORT_RANGE', 'SUM_SORT_ROWS', 'SUM_SORT_SCAN', 'SUM_NO_INDEX_USED',
                           'SUM_NO_GOOD_INDEX_USED']
            result = {}
            #查询每个field的topN数据，然后合并
            for item in items:
                cmd = 'select SCHEMA_NAME,DIGEST,'+','.join(self.fields)+\
                      ' from performance_schema.events_statements_summary_by_digest order by '+item +' desc limit '+str(self.topNum)
                rows = self.dataBaseInstance.execSql(cmd)
                for row in rows:
                    if str(row[0])+row[1] not in result.keys():
                        result[str(row[0])+row[1]] = row

            if result == {}:
                AgentLog.warning('TopSQLMonitor.doWork can not get topsql info')
                return

            for key,line in result.iteritems():
                if line[0] is None:  # 有schema为None的，这里取出来就是空了，为了下面的加法正确，将这个特殊值处理
                    statusBase = 'null' + "|" + line[1]
                else:
                    statusBase = line[0] + "|" + line[1]

                for index,val in enumerate(line[2:]):
                    status = statusBase + '|' + self.fields[index]
                    temp[status] = val
            self.lock.acquire()
            self.dataDict = temp
            self.lock.release()
        except Exception, e:
            raise e
