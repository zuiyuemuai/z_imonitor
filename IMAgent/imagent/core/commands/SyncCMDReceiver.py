#coding=utf-8
import threadpool

from imagent.core.commands.CommandReceiver import CommandReceiver
from imagent.core.commands.CommandFactory import CommandFactory
from imagent.core.communication.RabbitMQReceiver import RabbitMQReceiver
from imagent.core.communication.RabbitMQSender import RabbitMQSender
from imagent.core.common.AgentLog import AgentLog


def doWork(command, sender):
    # todo 线程池获取线程执行，不然会阻塞
    request = command.doWork()
    sender.send(request.getRequest())  # 发送到异步

#同步
class SyncCMDReceiver(CommandReceiver):
    pool = threadpool.ThreadPool(5)
    def __init__(self, context):
        self.context = context
        userConfig = context.userConfig
        sysConfig = context.systemConfig

         # 消息接收服务端,接收同步消息，parseMsg为定义的回调函数，参数为str类型
        receiver = RabbitMQReceiver(name_='SyncReceiver', host_=userConfig.get_rabbitmq_managerip(),
                                                 port_=userConfig.get_rabbitmq_rmqport(), exchange_=sysConfig.get_rabbitmq_exchange(),
                                                 queue_="{0}_sync_{1}".format(sysConfig.get_rabbitmq_listenQueue(),
                                                                               userConfig.get_agent_instanceid()),
                                                 routing_key_="sync_{0}".format(userConfig.get_agent_instanceid()))

        sender = RabbitMQSender(name_='Response', host_=userConfig.get_rabbitmq_managerip(),
                            port_=userConfig.get_rabbitmq_rmqport(),
                            exchange_=sysConfig.get_rabbitmq_exchange(),
                            routing_key_=sysConfig.get_rabbitmq_responseRouteKey())

        CommandReceiver.__init__(self, context, 'syncReceiverThread', receiver, sender)

    def doWork(self):
        self.receiver.receive(self.parseMsg, False)

    def parseMsg(self, response):
        AgentLog.debug("receive msg: {0}".format(response.body))
        try:
            try:
                command = CommandFactory.getCommand(response.getDBType(), response.getAction())(self.context, response)
            except AttributeError:
                request = self.createErrorRequest(response, 'command is not exist')
                self.sender.send(request.getRequest())
                return
            # request = command.doWork()
            # self.sender.send(request.getRequest())
            data = [((), {'command': command, 'sender': self.sender})]
            reqs = threadpool.makeRequests(doWork, data)
            [SyncCMDReceiver.pool.putRequest(req) for req in reqs]

        except Exception,e:
            AgentLog.error('syncCMDReceiver.parseMsg error %s'%e)