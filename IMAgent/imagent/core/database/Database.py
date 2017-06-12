# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-03
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""
from imagent.core.common.AgentAttrException import AgentAtrrException

class Database:
    def __init__(self, attr):
        try:
            self.config = attr
            self.user = attr['user']
            self.passwd = attr['passwd']
        except KeyError,e:
            raise AgentAtrrException('Database init KeyError:%s'%e)

    def getConnection(self,**kwargs):
        pass

    def shell(self,**kwargs):
        pass

    def isAlive(self):
        return "true"

    def backup(self, timestamp, backupType, binlogFile, backupTool):
        return True

    def getFile(self,dbFileName):
        try:
            return self.dbFiles[dbFileName].getFile()
        except KeyError:

            return None

    def getErrorLog(self, count, endRow):
        return ""

    def getVersion(self):
        return "mysql-5.5.30"
