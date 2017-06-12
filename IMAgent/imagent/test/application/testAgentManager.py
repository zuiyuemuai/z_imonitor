#coding=utf-8
import unittest

from imagent.core.application.AgentManager import AgentManager
from imagent.core.conf.AgentConfig import AgentConfig
from imagent.test.AgentTestCase import AgentTestCase


class AgentManagerTest(AgentTestCase):
    def setUp(self):
        super(AgentManagerTest,self).setUp()
        # AgentConfig.database={
        #      'name':'mysql',
        #      'attr':{}
        # }
    def tearDown(self):
        pass

    # def testCreateDB(self):
    #     AgentManager.createDB(AgentConfig.database)
    def testCreateInstance(self):
        AgentManager.createInstance(AgentConfig.agent)

if __name__ == '__main__':
    unittest.main()
