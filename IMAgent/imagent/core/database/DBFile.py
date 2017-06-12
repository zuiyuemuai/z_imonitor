#coding=utf-8
from imagent.core.common.Util import Util


class DBFile(object):
    def __init__(self, filePath):
        self.filePath = filePath

    def getFile(self, count, endRow):
        """
         获取path信息，startRow为开始行，endRow为结束行，
         endRow如果为-1，则代表endRow为最后一行
        """
        path, name = Util.pathSplit(self.filePath)
        if path == "":
            return False, "can not find dir"
        if not Util.isExists(self.filePath):
            return False, "file not exist"
        cmd = "sed -n '$=' %s" % self.filePath
        rows = long(Util.popen(cmd).readlines()[0])
        endRow = rows - endRow
        if endRow < 1:
            endRow = rows % count
        startRow = endRow - count
        if startRow < 0:
            startRow = 0
        cmd = "sed -n '%d,%d'p %s" % (startRow + 1, endRow, self.filePath)
        lines = Util.popen(cmd).readlines()
        return True, "".join(lines)
