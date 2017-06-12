# coding=utf-8
__author__ = 'hzluqianjie'

import re

from imagent.core.commands.Command import Command
from imagent.core.common.AgentLog import AgentLog
from imagent.core.communication.AgentRequst import AgentRequest

class MysqlShell(Command):
    """
    这个功能是想微信端直接发送sql命令来执行，并且返回
    Todo:功能未完善,check代码未完成
    """
    # 允许的命令
    allowCmdList = {'showHandle': re.compile('^show', re.I),
                    'selectHandle': re.compile('^select', re.I),
                    'descHandle': re.compile('^desc', re.I)}
    def __init__(self,context, response):
        Command.__init__(self,context,response)
        self.databaseInstance = context.dataBaseInstance


    def commonHandle(self):
        try:
            return self.databaseInstance.execSql(sql=self.cmd, db=self.db)
        except Exception, e:
            raise e

    def selectHandle(self):
        try:
            try:
                ret = re.findall('^select (.*?) from (.*?)$', self.cmd, re.I)[0]
                cmd = 'select count(' + ret[0] + ') from ' + ret[1]
                self.num = self.databaseInstance.execSql(sql=cmd, db=self.db)[0][0]
            except:  # 如果不匹配的话就直接填充0
                self.num = 0
            cmd = self.cmd
            if re.match('(.*)limit(.*)', self.cmd) is None:  # 如果已经有limit命令就不自动分页
                cmd = self.cmd + ' limit ' + str(self.offset) + ',' + str(self.limit)
            print cmd
            ret = self.databaseInstance.execSql(sql=cmd, db=self.db)
        except Exception, e:
            raise e
        return ret

    def showHandle(self):
        try:
            result = self.commonHandle()
            self.num = len(result)
            # 由于show不支持limit操作，所以这里编码实现
            if self.offset < self.num:
                if self.offset + self.limit >= self.num:
                    result = result[self.offset:]
                else:
                    result = result[self.offset:self.offset + self.limit]
            print result
            return result
        except Exception, e:
            raise e

    def descHandle(self):
        try:
            return self.commonHandle()
        except Exception, e:
            raise e


    def check(self):
        ret, msg = False, "check cmd error"
        params = self.response.getContent()
        if params == None:
            return False, "parameters not exist"

        self.cmd = params.get('cmd', None)
        self.db = params.get('db', None)
        self.offset = params.get('offset', 0)
        self.limit = params.get('max', 50)
        self.num = 1

        for handle, allowCmd in self.allowCmdList.iteritems():  # 权限判断，是否是能执行的命令
            if not allowCmd.match(self.cmd) == None:
                self.handle = getattr(self, handle)
                self.compile = allowCmd
                ret, msg = True, ""

        return ret, msg

    def errorHandler(self, msg):
        """
        错误信息的处理
        :return:
        """
        ret = re.findall('error:\((.*?)\)', msg)
        if len(ret) != 0:  # 不为0则说明sql执行错误
            return ret[0]
        return msg

    def doWork(self):
        isSuccess, errMsg = self.check()

        if not isSuccess:
            return self.responseFailed(errMsg)
        try:
            ret = self.handle()
        except Exception, e:
            AgentLog.error('MysqlShell.doWork error :%s'%e)
            ret = self.errorHandler("%s" % e)
            return self.responseFailed(ret)

        return self.responseOK(ret)

    def responseOK(self, msg):
        request = AgentRequest()
        request.setAction('response')
        request.setId(self.instanceID, self.groupID, self.clusterID)
        request.setSessionId(self.response.getSessionID())
        request.setContent({'status':True,'msg':msg,'num':self.num})
        return request

    def responseFailed(self, errMsg):
        request = AgentRequest()
        request.setAction('response')
        request.setId(self.instanceID, self.groupID, self.clusterID)
        request.setSessionId(self.response.getSessionID())
        request.setContent({'status':False,'msg':errMsg,'num':self.num})
        return request
