# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2014-12-25
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""
import sys

sys.path.append("..")

from imagent.core.application.daemon import Daemon
from imagent.core.common.AgentLog import AgentLog
from imagent.core.conf.AgentConfigManager import AgentConfigManager
from imagent.core.application.AgentOptionParser import AgentOptionParser
from imagent.core.common.Util import Util
from imagent.core.application.AgentManager import AgentManager


def main():
    agentManager = None
    try:

        # 解析命令行，获取配置文件地址和是否console执行
        optParser = AgentOptionParser()
        cfgFile = Util.getRealPath(optParser.configFile)
        console = optParser.console

        # 获取配置文件配置
        userConfig,sysConfig = AgentConfigManager.initAllConfig(cfgFile)

        # 如果为console状态，则直接运行，如果为非console状态，则在后台以daemon形式运行
        if not console:
            Daemon()
        else:
            userConfig.log['logSection'] = "debug"

        # 初始化日志句柄，所有相关日志的操作都需要放该操作后面
        AgentLog.init(userConfig.log['logConfig'], userConfig.log['logSection'])

        agentManager = AgentManager(userConfig, sysConfig)

        agentManager.start()

        while True:
            Util.sleep(5)

        agentManager.stop()

    except KeyboardInterrupt:
        if agentManager is not None:
            agentManager.stop()
    finally:
        if agentManager is not None:
            agentManager.stop()


if __name__ == '__main__':
    main()

