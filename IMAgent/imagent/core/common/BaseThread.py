# -*- coding:UTF-8 -*- 
"""
@author:  jianghongxiang
@date:    2014-12-30
@contact: jhx1008@gmail.com
version:  1.0
@todo:    线程基础类，用于定义线程的基础信息 
@modify:
"""

import time
import traceback
import threading

from imagent.core.common.AgentLog import AgentLog


class BaseThread(threading.Thread):
    def __init__(self, threadName, activeReportInterval=5.0, loopInterval=60):
        threading.Thread.__init__(self, name=threadName)
        self.isRunning = True
        # 线程循环间隔时间
        self.loopInterval = loopInterval
        # 线程每隔一段时间需要上报一次当前状态，activeReportInterval为上报间隔
        self.activeReportInterval = activeReportInterval
        self.lastReportTime = 0
        # 多数线程为循环线程，需要每个一定时间运行一次，通过event.wait()进行等待，
        # 采用event.wait而不是sleep的好处是，在线程退出时可以直接通过set命令取消等待，
        # 不需要等待sleep结束
        self.event = threading.Event()
        self.event.clear()
        AgentLog.info("thread [{0}] created, report interval: {1}, loop interval: {2}".format( \
            self.getName(), activeReportInterval, loopInterval))

    def run(self):
        AgentLog.info('thread {0} start running'.format(self.getName()))
        while self.isRunning:
            try:
                self.doWork()
                if self.lastReportTime == 0:
                    self.lastReportTime = int(time.time())
                # 获取当前时间
                currentTime = int(time.time())
                # 比较是否已经超时，如果超时，则在日志文件中打印线程alive信息
                if currentTime >= self.lastReportTime + self.activeReportInterval:
                    AgentLog.info(
                        ' thread:[{0}] is alive '.format(self.getName()).ljust(45, ' ').center(75, '#'))
                    self.lastReportTime = currentTime
            except Exception, e:
                AgentLog.error(
                    "thread [{0}] raise Exception: {1}".format(self.getName(), traceback.format_exc()))
            # 等待下一次运行
            self.event.wait(self.loopInterval)
        AgentLog.info('thread:{0} exit'.format(self.getName()))

    def doWork(self):
        pass

    def clear(self):
        pass

    def stop(self):
        AgentLog.info("wait thread: {0} to exit".format(self.getName()))
        self.isRunning = False
        self.event.set()
        self.join()
        self.clear()