#coding=utf-8
import unittest
import os
import re

from imagent.core.common.AgentLog import AgentLog
from imagent.core.conf import AgentConfig


class AgentTestCase(unittest.TestCase):
    def setUp(self):
        print 'init logging'
        nowPath = re.findall('(.*?)IMAgent\\\\test',os.getcwd())[0]
        self.configPath = nowPath+'IMAgent\\test\\conf\\'
        AgentLog.init(self.configPath+'logging.cnf')

        #正确配置
        AgentConfig.database = AgentConfig.database={
             'name':'Mysql',
             'attr':{
                 'user':'',
                 'passwd':'',
                 'home':'',
                 'configFile': 'test.cnf',
                 'backupDir':''
             }
        }

if __name__ == '__main__':
    unittest.main()