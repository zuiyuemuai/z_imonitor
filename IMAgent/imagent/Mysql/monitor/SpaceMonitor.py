# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-03
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""
from imagent.core.monitor.Monitor import Monitor


class SpaceMonitor(Monitor):
    """
    对于数据库大小的监控
    """
    def __init__(self, context, threadName="TopSQLMonitor"):
        interval = context.userConfig.get_monitors_interval()
        Monitor.__init__(self, context=context,alias='space', threadName=threadName,
                         activeReportInterval=interval['activeInterval'],
                         interval=interval['topsqlInterval']
                         )
        # self.topNum = context.userConfig.get_monitors_attr('TopSQLMonitor'.lower())['topn']
        # self.fields = context.userConfig.get_monitors_attr('TopSQLMonitor'.lower())['fields'].split(';')

        self.dataBaseInstance = context.dataBaseInstance

    def doWork(self):
        try:
            temp = {}



            cmd = "select TABLE_SCHEMA,concat(sum(data_length)), concat(sum(index_length)),concat(sum(data_length)+sum(index_length)) as a,concat(sum(table_rows)) from information_schema.tables group by TABLE_SCHEMA order by a desc"
            database_spaces = self.dataBaseInstance.execSql(cmd)


            for database in database_spaces:
                databaseName = database[0]
                temp[databaseName+'_data'] = database[1]
                temp[databaseName+'_index'] = database[2]
                temp[databaseName+'_total'] = database[3]
                temp[databaseName+'_line'] = database[4]
                cmd = "select TABLE_NAME,DATA_LENGTH,INDEX_LENGTH,(DATA_LENGTH + INDEX_LENGTH) as allD,TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA='"+databaseName+"' order by allD desc"
                table_spaces = self.dataBaseInstance.execSql(cmd)
                for table in table_spaces:
                    tableName = table[0]
                    temp[databaseName+'_'+tableName+'_data'] = table[1]
                    temp[databaseName+'_'+tableName+'_index'] = table[2]
                    temp[databaseName+'_'+tableName+'_total'] = table[3]
                    temp[databaseName+'_'+tableName+'_line'] = table[4]
            self.lock.acquire()
            self.dataDict = temp
            self.lock.release()
        except Exception, e:
            raise e
