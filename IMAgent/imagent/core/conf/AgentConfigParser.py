# -*- coding:UTF-8 -*- 
"""
@author:  jianghongxiang
@date:    2014-12-25
@contact: jhx1008@gmail.com
version:  1.0
@todo:    配置文件解析类，用于解析Agent的配置文件
@modify:
"""

import os
from ConfigParser import ConfigParser

from imagent.core.common.AgentException import AgentException


class AgentConfigParser(ConfigParser):
    """
     用于解析Agent的配置文件
    """

    def __init__(self, configFileName):
        """
         配置文件解析类初始化函数，configFileName为配置文件全路径，cmdDict为配置参数字典
        """
        if not os.path.isfile(configFileName):
            raise AgentException("config file {0} not exists".format(configFileName))

        try:
            self.cfgParser = ConfigParser()
            self.cfgParser.read(configFileName)
        except Exception, e:
            raise AgentException(e)

    def getSections(self):
        return self.cfgParser.sections()

    def getItems(self, section):
        return self.cfgParser.items(section)

    def getValue(self, section, option):
        try:
            return self.cfgParser.get(section, option)
        except:
            return None
