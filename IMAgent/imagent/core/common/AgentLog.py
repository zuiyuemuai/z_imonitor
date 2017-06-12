# -*- coding:UTF-8 -*- 
"""
@author:  jianghongxiang
@date:    2014-12-25
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""

import logging
import traceback
import logging.config

from imagent.core.common.AgentException import AgentException


class AgentLog:
    logger = None

    @staticmethod
    def init(config_file='log.cnf', section="normal"):
        try:
            logging.config.fileConfig(config_file)
            AgentLog.logger = logging.getLogger(section)
        except Exception, e:
            raise AgentException('Agent init Error:%s'%e)

    @staticmethod
    def debug(msg):
        try:
            AgentLog.logger.debug(msg)
        except AttributeError:
            raise AgentException('AgentLog has not inited')

    @staticmethod
    def info(msg):
        try:
            AgentLog.logger.info(msg)
        except AttributeError:
            raise AgentException('AgentLog has not inited')

    @staticmethod
    def warning(msg):
        try:
            AgentLog.logger.warning(msg+'stack:%s'%traceback.format_exc())
        except AttributeError:
            raise AgentException('AgentLog has not inited')

    @staticmethod
    def error(msg):
        try:
            AgentLog.logger.error(msg+'stack:%s'%traceback.format_exc())
        except AttributeError:
            raise AgentException('AgentLog has not inited')

    @staticmethod
    def critical(msg):
        try:
            AgentLog.logger.critical(msg+'stack:%s'%traceback.format_exc())
        except AttributeError:
            raise AgentException('AgentLog has not inited')
