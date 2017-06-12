#coding=utf-8

from imagent.core.common.BaseThread import BaseThread
from imagent.core.common.AgentLog import AgentLog
from imagent.core.communication.AgentRequst import AgentRequest

class MonitorSenderThread(BaseThread):
    def __init__(self, montorInstances, sender,filters, context, threadName='MonitorSenderThread'):
        uMonitorConfig = context.userConfig.monitors
        userConfig = context.userConfig
        BaseThread.__init__(self, threadName, uMonitorConfig['interval']['activeInterval'], uMonitorConfig['interval']['senderInterval'])
        self.montorInstances = montorInstances
        self.sender = sender
        self.filters = filters
        self.context = context

        self.instanceId = userConfig.get_agent_instanceid()
        self.groupId = userConfig.get_agent_groupid()
        self.clusterId = userConfig.get_agent_clusterid()

        self.isFirst = True

    def doWork(self):
        content = {}
        for name, monitor in self.montorInstances.iteritems():
            data = monitor.getData()
            if data == None:
                AgentLog.warning("MonitorSenderThread.doWork can not get the %s Info,size is 0, now skip this time"%name)
                return
            if len(data) == 0:
                AgentLog.warning("MonitorSenderThread.doWork can not get the %s Info,size is 0"%name)
                continue
            content = dict(content, **data)
        request = AgentRequest(content=content)
        request.setId(self.instanceId, self.groupId, self.clusterId)

        for filter in self.filters:
            request.setContent(filter.filter(request.getContent()))

        if not self.isFirst:
            self.sender.send(request.getRequest())
        else:
            self.isFirst = False