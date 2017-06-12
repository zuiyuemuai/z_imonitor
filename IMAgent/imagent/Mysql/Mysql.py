# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-03
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""

import re

from imagent.core.database.DBFile import DBFile
from imagent.core.database.Database import Database
from imagent.core.common.AgentAttrException import AgentAtrrException
from imagent.core.common.AgentException import AgentException
from imagent.core.common.Util import Util
from imagent.core.common.AgentLog import AgentLog
from imagent.core.common.AgentFileException import AgentFileException


class Mysql(Database):
    def __init__(self, attr):
        AgentLog.info('Start to init Mysql from config')
        Database.__init__(self, attr)
        try:
            self.installPath = attr['home']
            self.configFile = attr['config']
            self.backupDir = attr['backupdir']
            self.socket = self.getSocket()
            self.dataDir = self.getDataDir()
            self.binlogName = self.getBinlogName()
        except (KeyError, AgentAtrrException), e:
            raise AgentAtrrException('Mysql init KeyError:%s'%e)
        except AgentFileException, e:
            raise e

    def getConnection(self,**kwargs):
        import MySQLdb
        if kwargs.get('db') == None:
            return MySQLdb.connect(unix_socket=self.socket, user=self.user, passwd=self.passwd)
        else:
            return MySQLdb.connect(unix_socket=self.socket, user=self.user, passwd=self.passwd, db=kwargs.get('db'))

    def execSql(self, sql, db=None):
        try:
            conn = self.getConnection(db=db)
            conn.autocommit(True)
            cursor = conn.cursor()
            try:
                cursor.execute(sql)
                rows = cursor.fetchall()
                cursor.close()
                conn.close()
                return rows
            except Exception, e:
                cursor.close()
                raise AgentException("execute sql '%s' error:%s" % (sql, e))
        except Exception, e:
            raise AgentException("connect execute sql '%s' error:%s" % (sql, e))

    def getStatus(self):
        """
        """
        return self.execSql("show global status")

    def isAlive(self):
        try:
            self.getStatus()
            return 'true'
        except Exception,e:
            AgentLog.error('Mysql.isAlive failed, %s'%e)
            return "false"

    def getSlaveStatus(self):
        """
        """
        return self.execSql("show slave status")

    def getErrorLog(self, count, endRow):
        """
         获取error log信息，startRow为开始行，endRow为结束行，
         endRow如果为-1，则代表endRow为最后一行
        """
        errLog = self.getValue(self.configFile, "log_error")
        if errLog == "":
            errLog = self.getValue(self.configFile, "log-error")
        if errLog == "":
            return False, "error log not configure in mysql configure file"
        path, name = Util.pathSplit(errLog)
        if path == "":
            dataDir = self.getValue(self.configFile, "datadir")
            if dataDir == "":
                return False, "can not find data dir for mysql"
            else:
                errLog = "{0}/{1}".format(dataDir, errLog)
        if not Util.isExists(errLog):
            return False, "error log file not exist"
        cmd = "sed -n '$=' %s" % errLog
        rows = long(Util.popen(cmd).readlines()[0])
        endRow = rows - endRow
        if endRow < 1:
            endRow = rows % count
        startRow = endRow - count
        if startRow < 0:
            startRow = 0
        cmd = "sed -n '%d,%d'p %s" % (startRow + 1, endRow, errLog)
        lines = Util.popen(cmd).readlines()
        return True, "".join(lines)

    def getSlowLog(self, count, endRow):
        """
         获取slow log信息，startRow为开始行，endRow为结束行，
         endRow如果为-1，则代表endRow为最后一行
        """
        slowLog = self.getValue(self.configFile, "slow_query_log_file")
        if slowLog == "":
            slowLog = self.getValue(self.configFile, "slow-query-log-file")
        if slowLog == "":
            return False, "error log not configure in mysql configure file"
        path, name = Util.pathSplit(slowLog)
        if path == "":
            dataDir = self.getValue(self.configFile, "datadir")
            if dataDir == "":
                return False, "can not find data dir for mysql"
            else:
                slowLog = "{0}/{1}".format(dataDir, slowLog)
        if not Util.isExists(slowLog):
            return False, "error log file not exist"

        startRow = endRow - count
        if startRow < 0:
            startRow = 0
        cmd = "sed -n '%d,%d'p %s" % (startRow + 1, endRow, slowLog)
        lines = Util.popen(cmd).readlines()
        return True, "".join(lines)

    def backup(self, timestamp, backupType, binlogFile, backupTool):
        """
         利用innobackupex进行数据备份
        """
        backupDir = "{0}/{1}".format(self.backupDir, timestamp)
        Util.popen("mkdir -p {0}".format(backupDir))
        Util.popen("chmod 0755 {0}".format(backupDir))
        if backupType == "incremental":
            return self.backupBinlogInfo(backupDir, binlogFile)
        elif backupTool == "innobackupex" or backupTool == "xtrabackup":
            return self.backupByInnobackupex(backupDir)
        elif backupTool == "mysqldump":
            return self.backupByMysqldump(backupDir)

    def backupBinlogInfo(self, backupDir, startBinlog):
        binlogList = self.getLatestBinlogList(startBinlog)
        if len(binlogList) == 0:
            return False, '', '-1', 'binlog later than %s not found' % startBinlog, '-1'
        filestr = ' '.join(binlogList)
        lastBinlog = binlogList[-1]
        cmd = "tar czf {0}/{1}.tar.gz -C {2} {3}".format(backupDir, lastBinlog, self.dataDir, filestr)
        lines = Util.popen(cmd).readlines()
        if len(lines) != 0:
            return False, '', '-1', ' '.join(lines), '-1'
        fileSize = Util.getFileSize("{0}/{1}.tar.gz".format(backupDir, lastBinlog))
        return True, lastBinlog, '0', backupDir, '{0}'.format(fileSize)

    def getLatestBinlogList(self, startBinlog):
        cmd = "ls %s | grep %s | grep -v %s.index" % (self.dataDir, self.binlogName, self.binlogName)
        binlogNo = 0
        if startBinlog.find(self.binlogName) != -1:
            binlogNo = long(startBinlog.split('.')[1])
        binlogList = Util.popen(cmd).readlines()
        retList = []
        for item in binlogList:
            item = item.split('/')[-1]
            index = long(item.split('.')[1])
            if not index < binlogNo:
                retList.append("%s.%06d" % (self.binlogName, index))
        return retList

    def backupByInnobackupex(self, backupDir):
        isSuccess = False
        masterFile = ''
        masterPos = -1
        errMsg = ''
        fileSize = -1
        backupLog = "{0}/backup.log".format(backupDir)
        cmd = "innobackupex --lock-wait-timeout=3600 --lock-wait-threshold=5 --lock-wait-query-type=all " \
              "--defaults-file={0} --socket={1} --slave-info --stream=tar --user={2} --password={3} --tmpdir={4} {4} 2>{5} | gzip > {4}/backup.tar.gz".format(
            self.configFile,
            self.socket, self.user, self.passwd, backupDir, backupLog)
        lines = Util.popen(cmd).readlines()
        if len(lines) != 0:
            return isSuccess, masterFile, '{0}'.format(masterPos), ' '.join(lines), '{0}'.format(fileSize)
        fileSize = Util.getFileSize("{0}/backup.tar.gz".format(backupDir))
        isSuccess, masterFile, masterPos, errMsg = self.isBackupOK(backupLog)
        if isSuccess:
            errMsg = backupDir
        return isSuccess, masterFile, '{0}'.format(masterPos), errMsg, '{0}'.format(fileSize)

    def backupByMysqldump(self, backupDir):
        # mysqldump -A -R -E -uuser -ppassword --socket=...
        # -A: 导出全部数据库的数据
        # -R: 导出存储过程和函数
        # -E: 导出events
        # --master-data值为1或者2,如果设置为1则在load sql脚本的时候会自动执行change master，如果设置为2则需要手动执行
        # 其实就是change master在sql脚本中是否被注释了，1为不注释，2为被注释掉了
        # --dump-slave在slave上执行时，获取master上的位置，类似于innobackupex的--slave-info，如果在master上执行则会报错
        isSuccess = False
        masterFile = ''
        masterPos = -1
        errMsg = ''
        fileSize = -1
        #Start modified by hzluqianjie for IM-25 at 2016-1-12 新增了错误重定向
        cmd = "{0}/bin/mysqldump --user={1} --password={2} --socket={3} -A -E -R --master-data=2  1> {4}/backup.sql 2>{5}/error".format(
            self.installPath, self.user, self.passwd, self.socket, backupDir,backupDir)
        lines = Util.popen(cmd).readlines()
        if len(lines) != 0:
            return isSuccess, masterFile, '{0}'.format(masterPos), ' '.join(lines), '{0}'.format(fileSize)
        lines = Util.popen('cat {0}/error'.format(backupDir)).readline()
        if len(lines) != 0:
            #循环检查是否有Error，如果是Error的话返回失败
            for line in lines:
                if re.match('^mysqldump: Error:(.*?)', line, re.I):
                    return isSuccess, masterFile, '{0}'.format(masterPos), ' '.join(lines), '{0}'.format(fileSize)
        #End modified by hzluqianjie for IM-25 at 2016-1-12 新增了错误重定向

        cmd = "head -n 50 {0}/backup.sql".format(backupDir)
        lines = Util.popen(cmd).readlines()
        if len(lines) == 0:
            errMsg = "backup file not exist"
            return isSuccess, masterFile, '{0}'.format(masterPos), errMsg, '{0}'.format(fileSize)
        for line in lines:
            if line.find("CHANGE MASTER TO") != -1:
                line = line.split(';')[0]
                temp = line.split(',')
                masterFile = temp[0].split('=')[1]
                masterFile = masterFile.strip("'")
                masterPos = temp[1].split('=')[1]
                break
        if masterFile != '' and masterPos != -1:
            fileSize = Util.getFileSize("{0}/backup.sql".format(backupDir))
            isSuccess = True
            errMsg = backupDir
        else:
            errMsg = "can't get master info from backup file"
        return isSuccess, masterFile, '{0}'.format(masterPos), errMsg, '{0}'.format(fileSize)

    def isBackupOK(self, backupLog):
        """
         检查backup日志文件，查看备份是否正常结束
        """
        isSuccess = False
        masterFile = errInfo = ""
        masterPos = -1
        if not Util.isExists(backupLog):
            errInfo = "backup log [{0}] not exist".format(backupLog)
            return isSuccess, masterFile, masterPos, errInfo
        rePosition = re.compile("position[\s]+([0-9]+)")
        reFileName = re.compile("filename[\s]+\'([0-9a-z-.]+)\'", re.IGNORECASE)
        reErrInfo = re.compile("Error:([\s\S]+)", re.IGNORECASE)
        lines = Util.popen("tail -10 {0}".format(backupLog)).readlines()
        for line in lines:
            info = reErrInfo.search(line)
            if info != None:
                errInfo = info.group(1)
                break
            if line.find("innobackupex: completed OK!") != -1:
                isSuccess = True
                break
            info = reFileName.search(line)
            if info != None:
                masterFile = info.group(1)
            info = rePosition.search(line)
            if info != None:
                try:
                    masterPos = long(info.group(1))
                except:
                    masterPos = -1
        if not isSuccess:
            errInfo = ' '.join(lines)
        return isSuccess, masterFile, masterPos, errInfo

    def getVersion(self):
        sql = 'select version()'
        rows = self.execSql(sql)
        return rows[0][0]

    def getBinlogName(self):
        binlogName = self.getValue(self.configFile, "log-bin")
        if binlogName != "":
            return binlogName
        binlogName = self.getValue(self.configFile, "log_bin")
        if binlogName != "":
            return binlogName
        return "mysql-bin"

    def getSocket(self):
        socket = self.getValue(self.configFile, "socket")
        if socket == "":
            AgentLog.warning('Mysql can not get socket value from config, use /tmp/mysql.sock')
            socket = "/tmp/mysql.sock"
        return socket

    def getDataDir(self):
        dataDir = self.getValue(self.configFile, "datadir")
        if dataDir == "":
            AgentLog.warning('Mysql can not get datadir value from config, start get innodb_data_home_dir')
            dataDir = self.getValue(self.configFile, "innodb_data_home_dir")
        return dataDir

    def getValue(self, configFile, key):
        """
         从配置文件中获取指定key的值
        """
        if not Util.isExists(configFile):
            raise AgentFileException('Mysql can not find config File from path :%s'%configFile)
        try:
            with open(configFile, 'r') as f:
                for line in f:
                    if line.find(key) != -1:
                        key = (line.split('=')[0]).strip()
                        if key[0] != '#':
                            value = (line.split('=')[1]).strip()
                            print value
                            return value
        except IOError,e:
            raise AgentFileException('Mysql can not find config File from path :%s'%configFile)
        except Exception,e:
            AgentLog.warning('Mysql can not get Value from config, key: %s,configFile:%s'%(key,configFile))
        return ""

class SlowLogFile(DBFile):
    def getData(self):
        pass

class ErrorLogFile(DBFile):
    def getData(self):
        pass