#coding=utf-8

from imagent.core.application.AgentInstance import AgentInstance
from imagent.core.application.Manager import Manager
from imagent.core.common.AgentException import AgentException
from imagent.core.database.DataBaseManager import DataBaseManager
from imagent.core.common.Util import Util
from imagent.core.common.AgentAttrException import AgentAtrrException
from imagent.core.monitor.MonitorManager import MonitorManager
from imagent.core.application.AgentContext import AgentContext
from imagent.core.commands.CommandManager import CommandManager

class AgentManager(Manager):

    def __init__(self, userConfig, systemConfig):
        Manager.__init__(self, 'AgentManager')
        self.managers = []
        self.agentContext = self.createContext(userConfig, systemConfig)
        # 单实例运行，如果已经有一个进程存在时，再运行会自动退出
        self.agentInstance = self.createInstance(userConfig)

        self.agentMonitorManager = self.createMonitors(self.agentContext)
        self.managers.append(self.agentMonitorManager)

        self.commandManager = CommandManager(self.agentContext)
        self.managers.append(self.commandManager)

    def start(self):
        self.agentInstance.start()
        for manager in self.managers:
            manager.start()


    def stop(self):
        for manager in self.managers:
            manager.stop()
        self.agentInstance.stop()

    def createContext(self, userConfig, systemConfig):
        try:
            agentContext = AgentContext(userConfig, systemConfig)
            agentContext.instanceId = userConfig.get_agent_instanceid()
            agentContext.groupId = userConfig.get_agent_groupid()
            agentContext.clusterId = userConfig.get_agent_clusterid()
            agentContext.dataBaseInstance = self.createDB(userConfig.get_database_name(), userConfig.get_database_attr())
            return agentContext
        except KeyError,e:
            raise AgentAtrrException('AgentManager.createContext KeyError: %s'%e)
        except AgentException,e:
            raise e

    def createInstance(self, agentConfig):
        try:
            pidFile = '{0}/agent.pid'.format(agentConfig.get_agent_tmpdir())
            fileName = Util.pathSplit(__file__)[1]
            return AgentInstance(pidFile, fileName)
        except KeyError,e:
            raise AgentAtrrException('AgentManager.createInstance KeyError: %s'%e)


    def createDB(self, name, attr):
        try:
            return DataBaseManager.createDataBase(name, attr)
        except AgentException,e:
            raise e

    def createMonitors(self, context):
        try:
            return MonitorManager(context)
        except AgentException,e:
            raise e





