#coding=utf-8
import json

class AgentResponse(object):

    format={
        'timestamp':[],
        'head':['Action','Host','InstanceId','DBType', 'SessionId'],
        'content':[]
    }

    def check(self, jsonData):
        '''
        根据上面的模板对数据进行检查，判断是否数据都存在
        :param jsonData:
        :return:
        '''
        try:
            for item,itemValue in AgentResponse.format.iteritems():
                for value in itemValue:
                    a = jsonData[item][value]
        except KeyError,e:
            raise e
        return True


    def __init__(self,body):
        #数据解析
        try:
            data = json.loads(body)
            self.check(data)
        except KeyError,e:
            raise KeyError('AgentResponse check error %s data:%s'% (e, body))
        self.body = body
        self.timestamp = data.get('timestamp', None)
        self.head = data.get('head', None)
        self.content = data.get('content', None)
        self.body = body

    def getInstanceId(self):
        return self.head['InstanceId']

    def getTimeStamp(self):
        return self.timestamp

    def getHost(self):
        return self.head['Host']

    def getContent(self):
        return self.content

    def getDBType(self):
        return self.head['DBType']

    def getAction(self):
        return self.head['Action']

    def getSessionID(self):
        return self.head['SessionId']