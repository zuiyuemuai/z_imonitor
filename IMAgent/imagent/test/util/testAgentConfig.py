#coding=utf8

from imagent.test.AgentTestCase import AgentTestCase
from imagent.core.conf.AgentConfigManager import AgentConfigManager

class testConfig(AgentTestCase):
    def test(self):

        agentConfig,systemConfig = AgentConfigManager.initAllConfig(self.configPath+'agent.cnf')

        print agentConfig.database
        print agentConfig.agent
        print agentConfig.log
        print agentConfig.monitors
        print agentConfig.rabbitmq
        print systemConfig.monitors
        print systemConfig.rabbitmq


