#coding=utf-8
from imagent.core.common.Util import Util


class AgentRequest(object):
    headList = {'Action':'report', 'Host':' ', 'InstanceId':str(1), 'GroupId':str(1),
    'ClusterId':str(1),'DBType':'Mysql',
                'SessionId':0}
    def __init__(self,head={},content=[]):
        self.head = head
        self.content = content
        self.timestamp = Util.getTimeStr()
        for h,v in AgentRequest.headList.iteritems():
            if h not in head.keys():
                self.head[h] = v

    def setAction(self, action):
        self.head['Action'] = action

    def setDBType(self, type):
        self.head['DBType'] = type

    def setSessionId(self, id):
        self.head['SessionId'] = id

    def setId(self, instanceId, groupId, clusterId ):
        self.setInstanceId(instanceId)
        self.setGroupId(groupId)
        self.setClusterId(clusterId)

    def setInstanceId(self, id):
        self.head['InstanceId'] = id

    def setGroupId(self, id):
        self.head['GroupId'] = id

    def setClusterId(self, id):
        self.head['ClusterId'] = id

    def setHost(self, host):
        self.head['Host'] = host

    def setContent(self, content):
        self.content = content
    def getContent(self):
        return self.content

    def getRequest(self):
        # sys.getsizeof(msg)
        return Util.obj2Json(
            {'head':self.head, 'content':self.content, 'timestamp':self.timestamp})
