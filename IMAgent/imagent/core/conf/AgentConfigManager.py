__author__ = 'hzluqianjie'
from imagent.core.common.AgentException import AgentException
from imagent.core.conf.AgentConfig import AgentConfig,SystemConfig
from imagent.core.conf.AgentConfigParser import AgentConfigParser
from imagent.conf.system import system


class AgentConfigManager:

    @staticmethod
    def initConfig(path, config):
        cfgParser = AgentConfigParser(path)
        sections = cfgParser.getSections()
        for section in sections:
            if config.check(section) == None:
                raise AgentException("AgentConfigManager.initConfig unknown section {0}".format(section))
            items = cfgParser.getItems(section)
            for item in items:
                f = 'set_'+section+'_'+item[0].split('_')[0]
                try:
                    getattr(config, f)(item[0],item[1])
                except AttributeError:
                    raise AgentException("AgentConfigManager.initConfig unknown item {0}".format(item))

    @staticmethod
    def initSystemConfig(config):
        config.monitors= system['monitors']
        config.rabbitmq= system['rabbitmq']

    @staticmethod
    def initAllConfig(userPath):
        agentConfig = AgentConfig()
        systemConfig = SystemConfig()
        AgentConfigManager.initConfig(userPath, agentConfig)
        AgentConfigManager.initSystemConfig(systemConfig)
        return agentConfig,systemConfig

