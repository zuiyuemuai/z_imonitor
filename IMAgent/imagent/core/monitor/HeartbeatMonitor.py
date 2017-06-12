# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-04
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""
from imagent.core.monitor.Monitor import MonitorWithSender
from imagent.core.communication.AgentRequst import AgentRequest

class HeartbeatMonitor(MonitorWithSender):
    def __init__(self, context, sender, threadName="HeartbeatMonitor"):
        interval = context.userConfig.get_monitors_interval()
        MonitorWithSender.__init__(self, context=context, sender=sender, threadName=threadName,
                                   activeReportInterval=interval['activeInterval'],
                                   interval=interval['heartbeatInterval'])
        userConfig = context.userConfig
        self.instanceId = userConfig.get_agent_instanceid()
        self.groupId = userConfig.get_agent_groupid()
        self.clusterId = userConfig.get_agent_clusterid()

    def doWork(self):
        isAlived = self.context.dataBaseInstance.isAlive()
        content = {"isAlived": isAlived}
        request = AgentRequest(content=content)
        request.setId(self.instanceId, self.groupId, self.clusterId)
        request.setAction('heartbeat')
        self.sender.send(request.getRequest())
