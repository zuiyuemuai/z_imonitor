#coding=utf-8


import time

from imagent.core.commands.Command import Command
from imagent.core.common.AgentLog import AgentLog


class MysqlAWR(Command):
    def __init__(self, context, response):
        Command.__init__(self, context, response)
        self.db = context.dataBaseInstance

    def check(self):

        params = self.response.getContent()
        if params == None:
            return False, "parameters not exist"

        startTime = params.get('startTime', None)
        endTime = params.get('endTime', None)
        if startTime == None or endTime == None:
            return False, "error, pageNo or maxLines not exist"
        self.startTime = startTime
        self.endTime = endTime
        return True, ""

    def doWork(self):
        isSuccess, errMsg = self.check()
        if not isSuccess:
            return self.responseFailed(errMsg)
        endTime = self.endTime
        startTime = self.startTime
        instanceID = self.instanceID

        try:
            # 获取实例参数
            instanceData = self.getInstanceInfo(self.instanceID)

            # 获取时间参数
            elapsed = time.mktime(time.strptime(endTime, "%Y-%m-%d %H:%M")) - time.mktime(
                time.strptime(startTime, "%Y-%m-%d %H:%M"))
            if elapsed < 0:
                return self.responseFailed('TimeError')
            snapTime = {'BeginSnap': startTime, 'EndSnap': endTime, 'Elapsed': elapsed}

            # 获取全局参数
            showGlobal = self.db.execSql("show global variables")

            # 获取sql参数
            sqlData = self.getSQL(instanceID)

            # 获取状态参数
            # statusData = self.getLoadProfile(elapsed, startTime, endTime, instanceID)

            cacheProfile = self.getCacheProfile(instanceID)
            waitEvent = self.getWaitEvent(instanceID)

            ret = {'awr': {'Instance': instanceData,
                           'loadProfile': None, 'SnapTime': snapTime, 'CacheProfile': cacheProfile,
                           'WaitEvent': waitEvent, 'showGlobal': showGlobal, 'sql': sqlData
                           }}

            return self.responseOK(ret)

        except Exception, e:
            AgentLog.error('AWR get, error:%s' % (e))

    def getSqlAttr(self, lists, index):
        max = 0.00
        sum = 0.00
        min = float('+inf')

        for line in lists:
            try:
                value = float(line[index])
            except:
                continue
            if max < value: max = value
            if min > value: min = value
            sum += value
        return {'max': max, 'min': min, 'sum': sum, 'average': (sum / len(lists)), 'num': len(lists)}

    def getSQL(self, instanceID):

        baseCmd = "select * from performance_schema.events_statements_summary_by_digest order by "
        limit = ' limit 10'

        count = self.db.execSql(baseCmd + 'COUNT_STAR desc'+limit )

        timeWait = self.db.execSql( baseCmd + 'SUM_TIMER_WAIT desc'+limit)  # 前十条
        timeWaitAttr = self.getSqlAttr(timeWait, 4)

        lockTime = self.db.execSql( baseCmd + 'SUM_LOCK_TIME desc'+limit)  # 前十条
        lockTimeAttr = self.getSqlAttr(lockTime, 8)

        rowSent = self.db.execSql( baseCmd + 'SUM_ROWS_SENT desc'+limit)  # 前十条
        rowSentAttr = self.getSqlAttr(rowSent, 12)

        rowExamined = self.db.execSql(baseCmd + 'SUM_ROWS_EXAMINED desc'+limit)  # 前十条
        rowExaminedAttr = self.getSqlAttr(rowExamined, 13)

        rowAffected = self.db.execSql( baseCmd + 'SUM_ROWS_AFFECTED desc'+limit)  # 前十条
        rowAffectedAttr = self.getSqlAttr(rowAffected, 11)

        text = self.db.execSql( baseCmd + 'DIGEST_TEXT desc')  # 把所有的都取出来

        return {'SQLCount': count, 'SQLTimeWait': timeWait,
                'SQLLockTime': lockTime, 'SQLRowSent': rowSent, 'SQlRowExamined': rowExamined,
                'SQLAffected': rowAffected, 'Text': text,
                'attr': {'timeWait': timeWaitAttr, 'lockTime': lockTimeAttr, 'rowSent': rowSentAttr,
                         'rowExamined': rowExaminedAttr, 'rowAffected': rowAffectedAttr}}

    def getInstanceInfo(self, instanceId):

        try:

            ret = {'DBName': None, 'IP': None, 'Port': None}
            ret['version'] = self.db.execSql('select version()')[0][0]
            ret['schema'] = len(self.db.execSql('show databases'))
            ret['Uptime'] = self.db.execSql('show status like "Uptime"')[0][0]
            ret['Engine'] = 'Innodb'
            ret['NbCluster'] = 'NO'
            return ret
        except Exception, e:
            AgentLog.error("AWR getInstanceInfo error:%s" % e)

    def getCacheProfile(self, instanceId):

        try:
            ret = {}

            ret['PoolSize'] = int(self.db.execSql("show variables like 'innodb_buffer_pool_size'")[0][1]) / 1024 / 1024

            ret['RedologSize'] = int(self.db.execSql("show variables like 'innodb_log_file_size'")[0][1]) / 1024 / 1024

            # 获取hint
            answers = self.db.execSql("show status like 'innodb%_reads'")
            hint = {'Innodb_buffer_pool_reads': 0, 'Innodb_data_reads': 0}
            for line in answers:
                if line[0] in ('Innodb_buffer_pool_reads', 'Innodb_data_reads'):
                        hint[line[0]] = line[1]
            ret['Hint'] = float(hint['Innodb_buffer_pool_reads']) / float(hint['Innodb_data_reads'])
            return ret

        except Exception, e:
            AgentLog.error("AWR getCacheProfile error:%s" % e)

    def getWaitEvent(self, instanceId):
        ret = {}
        ret['TimedEvent'] = self.db.execSql("select EVENT_NAME,COUNT_STAR,SUM_TIMER_WAIT from performance_schema.events_waits_summary_global_by_event_name order by COUNT_STAR desc limit 10")
        return ret

