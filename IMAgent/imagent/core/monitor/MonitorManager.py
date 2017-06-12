# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-04
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""

from imagent.core.common.AgentLog import AgentLog
from imagent.core.common.AgentAttrException import AgentAtrrException
from imagent.core.communication.RabbitMQSender import RabbitMQSender
from imagent.core.monitor.MonitorSenderThread import MonitorSenderThread
from imagent.core.monitor.HeartbeatMonitor import HeartbeatMonitor
from imagent.core.monitor.SystemMonitor import SystemMonitor
from imagent.core.monitor.MonitorFilter import ReplaceFilter,IgnoreFilter
from imagent.core.application.Manager import Manager


class MonitorManager(Manager):

    def __init__(self, context):
        Manager.__init__(self, 'MonitorManager')
        self.senders = []
        self.filters = []
        self.monitorInstances = {}
        self.threads = []

        self.context = context
        userConfig = context.userConfig
        systemConfig = context.systemConfig

        print systemConfig.monitors
        #创建monitors
        self.monitorList = systemConfig.get_monitors(userConfig.get_database_name())

        self.monitorList.extend(userConfig.get_monitors_monitors())#合并用户monitor
        self.monitorList = list(set(self.monitorList))#去除重复元素
        self.monitorInstances = self.createMonitors(context, userConfig.get_database_name(),self.monitorList)
        self.threads = self.monitorInstances.values()

        #创建心跳监控
        hbSender = self.createSender(userConfig, systemConfig,'Heartbeat',systemConfig.get_rabbitmq_heartbeatRouteKey())
        self.senders.append(hbSender)
        self.heartBeatMonitor = HeartbeatMonitor(context=context, sender=hbSender)
        self.threads.append(self.heartBeatMonitor)


        #创建系统监控
        systemMonitor = SystemMonitor(context)
        self.monitorInstances['SystemMonitor'] = systemMonitor
        self.threads.append(systemMonitor)

        #创建过滤器
        self.filters.append(ReplaceFilter(userConfig.get_monitors_replace()))
        self.filters.append(IgnoreFilter(userConfig.get_monitors_ignore()))

        #创建发送者
        sender = self.createSender(userConfig, systemConfig, 'Monitor', systemConfig.get_rabbitmq_monitorRouteKey())
        self.senders.append(sender)
        senderThread = MonitorSenderThread(self.monitorInstances, sender, self.filters, context)
        self.threads.append(senderThread)

    def start(self):
        for thread in self.threads:
            thread.start()

    def stop(self):
        #停止所有线程
        for thread in self.threads:
            thread.stop()
        #关闭所有管道
        for sender in self.senders:
            sender.uninit()

    def createSender(self, uConfig, sConfig, sendName, keyName):
        return RabbitMQSender(name_=sendName, host_=uConfig.get_rabbitmq_managerip(),
                            port_=uConfig.get_rabbitmq_rmqport(),
                            exchange_=sConfig.get_rabbitmq_exchange(),
                            routing_key_=keyName)

    def createMonitors(self,context, dbName, monitorList):

        if isinstance(monitorList, list) is not True:
            raise AgentAtrrException('MonitorManager.createMonitors invalid monitorList')
        AgentLog.info('start to create monitors :%s'%(','.join(monitorList)))


        try:
            monitorInstances = {}
            base = 'from imagent.'+ dbName
            for monitor in monitorList:
                url = base+'.monitor.'+monitor+' import '+monitor
                exec url
                monitorInstances[monitor] = eval(monitor)(context)
            return monitorInstances
        except AttributeError,e:
            raise AgentAtrrException('MonitorManager.createMonitors can not get monitor :%s'%e)
        except SyntaxError,e:
            raise e




