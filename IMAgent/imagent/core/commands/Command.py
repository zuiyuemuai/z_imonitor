# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-14
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""
from imagent.core.communication.AgentRequst import AgentRequest

class Command:
    def __init__(self,context, response):
        self.response = response
        self.context = context
        self.databaseInstance = context.dataBaseInstance
        self.instanceID = context.userConfig.get_agent_instanceid()
        self.groupID = context.userConfig.get_agent_groupid()
        self.clusterID = context.userConfig.get_agent_clusterid()
        self.Action = 'response'
        self.DBType = 'Mysql'

    def check(self):
        pass

    def doWork(self):
        pass

    def responseOK(self, msg):
        request = AgentRequest()
        request.setAction(self.Action)
        request.setDBType(self.DBType)
        request.setId(self.instanceID, self.groupID, self.clusterID)
        request.setSessionId(self.response.getSessionID())
        request.setContent({'status':True,'msg':msg})
        return request

    def responseFailed(self, errMsg):
        request = AgentRequest()
        request.setAction(self.Action)
        request.setDBType(self.DBType)
        request.setId(self.instanceID, self.groupID, self.clusterID)
        request.setSessionId(self.response.getSessionID())
        request.setContent({'status':False,'msg':errMsg})
        return request
    def responseACK(self):
        request = AgentRequest()
        request.setAction(self.Action)
        request.setDBType(self.DBType)
        request.setId(self.instanceID, self.groupID, self.clusterID)
        request.setSessionId(self.response.getSessionID())
        request.setContent({'status':True,'msg':'ack'})
        return request