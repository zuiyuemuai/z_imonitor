# -*- coding: UTF-8 -*-
"""
@author:  jianghongxiang
@date:    2014-12-25
@contact: jhx1008@gmail.com
@versio:  1.0
@todo:
@modify:
"""
import os
import sys

from imagent.core.common.AgentException import AgentException
from imagent.core.common.AgentLog import AgentLog


class AgentInstance():
    """
     定义一个类AgentInstance，用于在同一时刻，只有 一个Agent进程可以运行
    """
    def __init__(self, pidFile, name="main.py"):
        """
         类初始化函数，参数pidFile为pid文件保存的位置
        """
        self.__pidFile__ = pidFile
        self.__fileName__ = name
        self.check()

    def check(self):
        """
         检测进程是否存在，检测方法：
         1.检测pid文件是否存在，如果不存在，则说明进程没有运行，新进程可以运行
         2.如果pid文件存在，则读取pid文件中的pid，在所有进程中查找文件中的pid的进程是否存在，
           如果进程存在，则新的进程不能运行，直接退出，如果进程不存在，说明可能是由于非正常退出(如：CTRL + C)
           造成pid文件未被清理，这种情况下，agent可以启动，先删除失效的pid文件，然后启动新的进程即可。
        """
        if not os.path.isfile(self.__pidFile__):
            return
        pid = 0
        try:
            file = open(self.__pidFile__, 'rt')
            data = file.read()
            file.close()
            # 获取文件中的pid进程号
            pid = int(data)
            if not self.isAlive(pid):
                try:
                    os.remove(self.__pidFile__)
                    return
                except:
                    AgentLog.warning("remove pid file {0} failed.".format(self.__pidFile__))
        except:
            pass
        AgentLog.info("agent exist, only one process allow running")
        sys.exit(1)

    def isAlive(self, pid):
        """
         在当前进程列表中，检查指定的pid，通过ps获取所有pid号，循环遍历所有pid号，
         找到与指定pid号匹配的进程，返回True，如果没有找到匹配的pid，返回False,
         当然这种判断不是万能的，如果当agent退出了，另外一个进程的pid正好等于agent保存的pid，
         并且当前系统中存在一个main.py运行的python程序，则可以导致没有Agent存在，而实际无法启动Agent
         的情况，鉴于这种概率比较小，而且发生时可以通过删除pid文件的方式来避免，所以如此设计
        """
        try:
            pids = os.popen(
                "ps -ef | grep '%s' | grep -v grep | awk -F' ' '{print $2}'" % self.__fileName__).readlines()
            # 循环遍历进程列表，查找匹配的进程号
            for _pid in pids:
                # remove the '\n' in the end
                _pid = _pid[0:-1]
                if _pid != "PID" and pid == int(_pid):
                    return True
            return False
        except Exception, e:
            return False

    def start(self):
        """
         把进程pid写入到对应的pid文件
        """
        AgentLog.info("RDS Agent start to run")
        try:
            file = open(self.__pidFile__, 'wt')
            file.write(str(os.getpid()))
            file.close()
        except:
            AgentLog.error("open pid file {0} error, start failed".format(self.__pidFile__))
            raise AgentException("open pid file {0} failed".format(self.__pidFile__))

    def stop(self):
        """
         程序退出时调用，在进程退出时，删除pid文件
        """
        AgentLog.info("RDS Agent start to exit")
        try:
            os.remove(self.__pidFile__)
        except:
            AgentLog.warning("remove pid file {0} error".format(self.__pidFile__))
            raise AgentException("remove pid file {0} error".format(self.__pidFile__))

