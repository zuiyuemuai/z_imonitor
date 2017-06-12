# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2014-12-25
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""
from imagent.core.common.AgentException import AgentException


class SystemConfig:
    MONITORS_Mysql = 'Mysql'
    MONITORS_Oracle = 'Oracle'
    MONITORS_Redis = 'Redis'
    MONITORS_Mongodb = 'Mongodb'

    RABBITMQ_EXCHAGE = 'exchange'
    RABBITMQ_MONITORROUTEKEY = 'monitorRouteKey'
    RABBITMQ_RESPONSEROUTEKEY = 'responseRouteKey'
    RABBITMQ_HBROUTEKEY = 'heartbeatRouteKey'
    RABBITMQ_LISTENQUEUE = 'listenQueue'

    def __init__(self):
        # 对于不同数据监控类加载
        self.monitors = {},
        self.rabbitmq = {}

    def get_monitors(self,name):
        return self.monitors[name]

    def get_rabbitmq_exchange(self):
        return self.rabbitmq['exchange']

    def get_rabbitmq_monitorRouteKey(self):
        return self.rabbitmq['monitorRouteKey']

    def get_rabbitmq_responseRouteKey(self):
        return self.rabbitmq['responseRouteKey']

    def get_rabbitmq_asyncResponseRouteKey(self):
        return self.rabbitmq['asyncRouteKey']

    def get_rabbitmq_heartbeatRouteKey(self):
        return self.rabbitmq['heartbeatRouteKey']

    def get_rabbitmq_listenQueue(self):
        return self.rabbitmq['listenQueue']

class AgentConfig:
    AGENT_TMPDIR = 'tmpDir'
    AGENT_INSTANCEID = 'instanceID'
    AGENT_GROUPID = 'groupID'
    AGENT_CLUSTERID = 'clusterID'
    DATABASE_NAME = 'name'
    DATABASE_ATTR = 'attr'
    MONITORS_MONITORS = 'monitors'
    MONITORS_AVERAGE = 'average'
    MONITORS_INTERVAL = 'interval'
    MONITORS_REPLACE = 'replace'
    MONITORS_IGNORE = 'ignore'
    RABBITMQ_IP = 'managerIP'
    RABBITMQ_PROT = 'rmqPort'

    def __init__(self):
        # [agent]
        self.agent = {
            'tmpDir': '/tmp',
            'instanceID': 1,
            'groupID': 1,
            'clusterID': 1}



        # [log]
        self.log = {
            'logConfig': 'log.cnf',
            'logSection': 'normal'
        }

        # [mysql]
        self.database = {
            'name': 'Mysql',
            'attr': {
                'user': '',
                'passwd': ''
            }
        }

        self.monitors = {
            'monitors': [],
            'attr':{

            },
            # 'average': {
            #     'mysqlStatus': '',
            #     'mysqlSlave': ''
            # },
            'interval': {
                'senderInterval': 30,
                'activeInterval': 300,
                'systemInterval': 20,
                'statusInterval': 20,
                'slaveInterval': 20,
                'topsqlInterval': 20,
                'heartbeatInterval': 10
            },
            # [replace]
            'replace': {},
            # [ignore]
            'ignore': []
        }

        # [communication]
        self.rabbitmq = {
            'managerIP': '127.0.0.1',
            'rmqPort': 5672
        }

    def check(self, section):
        return getattr(self, section, None)

    def set_agent_instanceid(self, key, id):
        self.agent['instanceID'] = int(id)

    def set_agent_groupid(self, key, id):
        self.agent['groupID'] = int(id)

    def set_agent_clusterid(self, key, id):
        self.agent['clusterID'] = int(id)

    def set_agent_tmpdir(self, key, tmpdir):
        self.agent['tmpDir'] = tmpdir

    def set_log_config(self, key, config):
        self.log['logConfig'] = config

    def set_log_section(self, key, section):
        self.log['logSection'] = section

    def set_database_name(self, key, name):
        self.database['name'] = name

    def set_database_attr(self, key, attr):
        keys = key.split('_')
        if len(keys) != 2:
            raise AgentException('setDBAttr unknown attr')
        self.database['attr'][keys[1]] = attr

    def set_monitors_interval(self, key, interval):
        keys = key.split('_')
        if len(keys) != 2:
            raise AgentException('setMonitorsInterval unknown attr')
        self.monitors['interval'][keys[1]] = interval

    def set_monitors_monitors(self, key, monitors):
        monitors = monitors.split(';')
        for monitor in monitors:
            self.monitors['monitors'].append(monitor)

    def set_monitors_replace(self, key, replace):
        pairs = replace.split(';')
        for keyValue in pairs:
            key, value = keyValue.split('|')
            # modified by luqianjie at 2015/10/26 for 配置文件的替换项如果出现相同的key，原来代码会将这些配置覆盖，下面用list传入
            if not key in self.monitors['replace']:
                self.monitors['replace'][key] = [value]
            else:
                self.monitors['replace'][key].append(value)
    def set_monitors_attr(self, key, val):
        keys = key.split('_')
        if len(keys) < 2:
            raise AgentException('setMonitorsInterval unknown attr')
        if keys[1] not in self.monitors['attr'].keys():
            self.monitors['attr'][keys[1]] = {keys[2]:val}
        else:
            self.monitors['attr'][keys[1]][keys[2]]=val

    def set_monitors_ignore(self, key, ignore):
        items = key.split(';')
        for item in items:
            self.monitors['ignore'].append(item)

    def set_rabbitmq_managerip(self,key,val):
        self.rabbitmq['managerIP'] = val

    def set_rabbitmq_rmqport(self,key,val):
        self.rabbitmq['rmqPort'] = int(val)


    def get_rabbitmq_managerip(self):
        return self.rabbitmq['managerIP']

    def get_rabbitmq_rmqport(self):
        return self.rabbitmq['rmqPort']

    def get_agent_instanceid(self):
        return self.agent['instanceID']

    def get_agent_groupid(self):
        return self.agent['groupID']

    def get_agent_clusterid(self):
        return self.agent['clusterID']

    def get_agent_tmpdir(self):
        return self.agent['tmpDir']

    def get_log_config(self):
        return self.log['logConfig']

    def get_log_section(self):
        return self.log['logSection']

    def get_database_name(self):
        return self.database['name']

    def get_database_attr(self):
        return self.database['attr']

    def get_monitors_interval(self):
        return self.monitors['interval']

    def get_monitors_monitors(self):
        return self.monitors['monitors']

    def get_monitors_replace(self):
        return self.monitors['replace']

    def get_monitors_attr(self, Name):
        return self.monitors['attr'][Name]

    def get_monitors_ignore(self):
        return self.monitors['ignore']


