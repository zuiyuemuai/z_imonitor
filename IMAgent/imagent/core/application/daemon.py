# -*- coding:UTF-8 -*- 
"""
@author:  jianghongxiang
@date:    2014-12-25
@contact: jhx1008@gmail.com
version:  1.0
@todo:    守护进程
@modify:
"""
import os
import sys

from imagent.core.common.AgentException import AgentException


class Daemon:
    def __init__(self):
        self.__start__()

    def __start__(self):
        try:
            if os.fork() > 0:
                sys.exit(0)
        except OSError, e:
            raise AgentException("fork #1 failed: %d (%s)" % (e.errno, e.strerror))
        os.chdir("/")
        os.setsid()
        os.umask(0)
        try:
            if os.fork() > 0:
                sys.exit(0)
        except OSError, e:
            raise AgentException("fork #2 failed: %d (%s)" % (e.errno, e.strerror))

        sys.stdout.flush()
        sys.stderr.flush()

        si = file('/dev/null', 'r')
        so = file('/dev/null', 'a+')
        se = file('/dev/null', 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
