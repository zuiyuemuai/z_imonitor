# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-03-24
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""

from imagent.core.common.BaseThread import BaseThread
from imagent.core.communication.AgentRequst import AgentRequest

class CommandReceiver(BaseThread):
    def __init__(self,context, threadName, receiver, sender):
        BaseThread.__init__(self, threadName=threadName,activeReportInterval=60,loopInterval=0)
        self.receiver = receiver
        self.sender = sender

        self.instanceID = context.userConfig.get_agent_instanceid()
        self.groupID = context.userConfig.get_agent_groupid()
        self.clusterID = context.userConfig.get_agent_clusterid()

    def doWork(self):
        self.receiver.receive(self.parseMsg, False)

    def start(self):
        BaseThread.start(self)

    def stop(self):
        BaseThread.stop(self)
        self.receiver.uninit()

    def parseMsg(self, response):
        pass

    def createErrorRequest(self, response, errMsg):
        request = AgentRequest()
        request.setAction('response')
        request.setId(self.instanceID, self.groupID, self.clusterID)
        request.setSessionId(response.getSessionID())
        request.setContent({'status':False,'msg':errMsg})
        return request