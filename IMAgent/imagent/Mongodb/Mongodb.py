# coding=utf-8

from imagent.core.database.Database import Database
from imagent.core.common.Util import Util


class Mongodb(Database):
    def __init__(self, attr):
        Database.__init__(self, attr)
        self.client = self.getClient()

    def getClient(self):
        # return pymongo.MongoClient("106.2.60.126",32837)
        return None

    # def execShell(self, sql, db=None):
    #     client = self.getClient()
    #     print client.database_names()
    #     db = client.test_database #连接库


    def getDatabases(self):
        client = self.client
        return client.database_names()

    def getDatabaseStatus(self, dbName):
        pass

    # 获取服务器信息，主要是版本信息、连接信息等，大部分都是str类型
    def getServerStatus(self):
        client = self.client
        print client.server_info()

    # 通过mongostat获取信息，但是会阻塞，阻塞时间在于line的大小
    def getMongoStat(self, line):
        cmd = "mongostat --json --rowcount %d" % (line)
        lines = Util.popen(cmd).readlines()
        return lines


# client = pymongo.MongoClient("106.2.60.126", 32846)
# print client.server_info()


