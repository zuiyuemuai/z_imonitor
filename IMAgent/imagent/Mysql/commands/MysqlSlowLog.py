# -*- coding:UTF-8 -*-
__author__ = 'hzluqianjie'

from imagent.core.commands.Command import Command


class MysqlSlowLog(Command):
    def __init__(self, context, params):
        Command.__init__(self, context, params)
        self.db = context.dataBaseInstance
        self.Action = 'MysqlSlowLog'

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

        isSuccess,errLog = self.db.getSlowLog(maxLines, endRow)

        if not isSuccess:
            return self.responseFailed(errLog)
        return self.responseOK(errLog)


