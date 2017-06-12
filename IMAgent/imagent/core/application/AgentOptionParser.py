# -*- coding:UTF-8 -*- 
"""
@author:  jianghongxiang
@date:    2014-12-25
@contact: jhx1008@gmail.com
version:  1.0
@todo:    该类用于解析Agent中的命令行参数，命令行参数解析放在配置文件解析之后，可以覆盖配置文件的配置
@modify:
"""

from optparse import OptionParser

from imagent.core.common.AgentException import AgentException


class AgentOptionParser(OptionParser):
    """
      命令行参数解析类
    """

    def __init__(self):
        """
         命令行解析类，命令行参数优先于配置文件：如果相同一个参数，既在配置文件中配置了，
         又在命令行参数中进行了设置，则命令行参数的设置将覆盖配置文件中的配置
        """
        usage = "usage: %prog [-option]"
        parser = OptionParser(usage)
        parser.add_option("-c", "--console", action="store_true", dest="console", help="前台运行")
        parser.add_option("-f", "--defaults-file", dest="configFile", help="指定agent的配置文件")
        self.configFile = "/etc/IMAgent/agent.cnf"
        self.console = False

        try:
            (options, args) = parser.parse_args()

            if options.console:
                self.console = options.console

            if options.configFile:
                self.configFile = options.configFile

        except SystemExit, e:
            raise AgentException(e)
