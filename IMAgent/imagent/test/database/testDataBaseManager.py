#coding=utf-8
import unittest

from imagent.test.AgentTestCase import AgentTestCase
from imagent.core.database.DataBaseManager import DataBaseManager
from imagent.core.conf.AgentConfig import AgentConfig


class DataBaseManagerTest(AgentTestCase):
    def setUp(self):
        super(DataBaseManagerTest, self).setUp()
        AgentConfig.database = AgentConfig.database={
             'name':'Mysql',
             'attr':{}
        }
    def testCreateDataBase(self):
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
        DataBaseManager.createDataBase(AgentConfig.database)
        # #错误配置
        # AgentConfig.database = AgentConfig.database={
        #      'name':'mysql',
        #      'attr':{}
        # }
        # DataBaseManager.createDataBase(AgentConfig.database)

if __name__ == "__main__":
    unittest.main()

