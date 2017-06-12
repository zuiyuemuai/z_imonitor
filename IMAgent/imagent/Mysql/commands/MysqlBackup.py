# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-14
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""
import os
import time
from ftplib import FTP

from imagent.core.common.Util import Util
from imagent.core.commands.Command import Command
from imagent.core.common.AgentLog import AgentLog


class MysqlBackup(Command):
    BACKUP_TYPE_LIST = ['full', 'incremental']
    BACKUP_TOOL_LIST = ['innobackupex', 'mysqldump', 'xtrabackup']

    def __init__(self, context, response):
        Command.__init__(self, context, response)
        self.db = context.dataBaseInstance
        self.Action = 'MysqlBackup'

    def check(self):

        params = self.response.getContent()
        if params == None:
            return False, "parameters not exist"
        self.params = params
        backupType = params.get('type', 'unknown')
        backupTool = params.get('tool', 'unknown')
        if backupType not in MysqlBackup.BACKUP_TYPE_LIST:
            return False, "unknown backup type {0}".format(backupType)
        if backupTool not in MysqlBackup.BACKUP_TOOL_LIST:
            return False, "unknown backup tool {0}".format(backupTool)
        self.backupType = backupType
        self.backupTool = backupTool
        self.binlogFile = ''
        if self.backupType == 'incremental':
            self.binlogFile = params.get('binlogFile', None)
            if self.binlogFile == None:
                return False, "incremental backup has error binlog file"
        return True, ""

    def doWork(self):
        isSuccess, errMsg = self.check()
        if not isSuccess:
            return self.responseFailed(errMsg)
        timestamp = self.response.getTimeStamp()
        timestamp = time.mktime(time.strptime(timestamp,'%Y-%m-%d %H:%M:%S'))
        try:
            isSuccess, masterFile, masterPos, errMsg, fileSize = self.db.backup(timestamp, self.backupType, self.binlogFile,
                                                                            self.backupTool)
        except Exception,e:
            isSuccess = False
            errMsg = 'Error %s'%e
            AgentLog.error(errMsg)

        if not isSuccess:
            return self.responseFailed(errMsg)
        isSuccess, errMsg = self.upload(errMsg)
        if not isSuccess:
            return self.responseFailed(errMsg)
        return self.responseOK(masterFile, masterPos, fileSize)

    def upload(self, srcDir):
        isSuccess = True
        errmsg = ''
        params = self.params
        transmitType = params.get('transmitType', None)
        if transmitType == 'ssh' or transmitType == 'scp':
            isSuccess, errmsg = self.upload_scp(params, srcDir)
        elif transmitType == 'ftp':
            isSuccess, errmsg = self.upload_ftp(params, srcDir)
        else:
            pass
        return isSuccess, errmsg

    def upload_scp(self, params, srcDir):
        remoteHost = params.get('remoteHost', None)
        remotePort = params.get('remotePort', None)
        remoteUser = params.get('remoteUser', None)
        remotePasswd = params.get('remotePassword', None)
        backupPath = params.get('backupPath', None)
        uploadLimit = params.get('uploadLimit', None)
        if remoteHost == None or remotePort == None or remoteUser == None or \
                        remotePasswd == None or backupPath == None or uploadLimit == None:
            return False, 'remote host information errors'
        uploadLimit = long(uploadLimit)
        AgentLog.info("start upload backup data to remote server")
        cmd = "scp -r -P %s %s %s@%s:%s" % (remotePort, srcDir, remoteUser, remoteHost, backupPath)
        if uploadLimit > 0:
            cmd = "scp -r -P %s -l %d %s %s@%s:%s" % (
                remotePort, uploadLimit * 8, srcDir, remoteUser, remoteHost, backupPath)
        lines = Util.popen(cmd).readlines()
        if len(lines) != 0:
            return False, ' '.join(lines)
        return True, ''

    def upload_ftp(self, params, srcDir):
        remoteHost = params.get('remoteHost', None)
        remotePort = params.get('remotePort', None)
        remoteUser = params.get('remoteUser', None)
        remotePasswd = params.get('remotePassword', None)
        backupPath = params.get('backupPath', None)
        uploadLimit = params.get('uploadLimit', None)
        if remoteHost == None or remotePort == None or remoteUser == None or \
                        remotePasswd == None or backupPath == None or uploadLimit == None:
            return False, 'remote host information errors'
        AgentLog.info("start upload backup data to ftp server")
        try:
            ftp = FTP()
            ftp.connect(remoteHost, int(remotePort), 60)
        except Exception, e:
            return False, 'can not connect to remote host: %s with port: %s, error: %s' % (remoteHost, remotePort, e)
        try:
            ftp.login(remoteUser, remotePasswd)
            ftp.cwd(backupPath)
            srcDir = srcDir.rstrip('/')
            localName = Util.pathSplit(srcDir)[1]
            ftp.mkd(localName)
            self.uploadDir(ftp, srcDir, localName)
            AgentLog.info("upload completely")
        except Exception, e:
            return False, 'upload error, error:%s' % e
        finally:
            ftp.quit()
        return True, ''

    def uploadDir(self, ftp, localDir, remoteDir):
        ftp.cwd(remoteDir)
        for file in os.listdir(localDir):
            src = os.path.join(localDir, file)
            if os.path.isfile(src):
                ftp.storbinary('STOR ' + file, open(src, 'rb'))
            elif os.path.isdir(src):
                ftp.mkd(file)
                self.uploadDir(ftp, src, file)
        ftp.cwd('..')

    def responseOK(self, masterFile, masterPos, fileSize):
        context = {'errorMsg': '', 'size': '{0}'.format(fileSize)}
        context['backupId'] = self.params['backupId']
        context['masterFile'] = masterFile
        context['masterPos'] = '{0}'.format(masterPos)
        context['gtid'] = ''
        return Command.responseOK(self, context)

    def responseFailed(self, errMsg):
        context = {'errorMsg':errMsg}
        context['backupId'] = self.params['backupId']
        return Command.responseFailed(self, context)