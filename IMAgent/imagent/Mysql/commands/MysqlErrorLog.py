# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-19
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""

from imagent.core.commands.Command import Command


class MysqlErrorLog(Command):
    def __init__(self, context, response):
        Command.__init__(self, context, response)
        self.db = context.dataBaseInstance

    def check(self):

        params = self.response.getContent()
        if params == None:
            return False, "parameters not exist"

        pageNo = params.get('pageNo', None)
        maxLines = params.get('maxLines', None)
        if maxLines == None or pageNo == None:
            return False, "error, pageNo or maxLines not exist"
        self.pageNo = pageNo
        self.maxLines = maxLines
        return True, ""

    def doWork(self):
        isSuccess, errMsg = self.check()
        if not isSuccess:
            return self.responseFailed(errMsg)

        pageNo = long(self.pageNo)
        maxLines = long(self.maxLines)
        endRow = (pageNo - 1) * maxLines

        isSuccess,errLog = self.db.getErrorLog(maxLines, endRow)

        if not isSuccess:
            return self.responseFailed(errLog)
        return self.responseOK(errLog)


