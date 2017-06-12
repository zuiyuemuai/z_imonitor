# coding=utf-8
import threadpool

from imagent.core.commands.CommandReceiver import CommandReceiver
from imagent.core.communication.RabbitMQReceiver import RabbitMQReceiver
from imagent.core.communication.RabbitMQSender import RabbitMQSender
from imagent.core.common.AgentLog import AgentLog
from CommandFactory import CommandFactory


def doWork(command, asyncSender):
    # todo 线程池获取线程执行，不然会阻塞
    request = command.doWork()
    asyncSender.send(request.getRequest())  # 发送到异步


class AsyncCMDReceiver(CommandReceiver):
    pool = threadpool.ThreadPool(5)

    def __init__(self, context):
        userConfig = context.userConfig
        systemConfig = context.systemConfig
        self.context = context

        # 消息接收服务端，接收异步消息，parseMsg为定义的回调函数，参数为str类型
        rabbitMQAsyncReceiver = RabbitMQReceiver(name_='AsyncReceiver', host_=userConfig.get_rabbitmq_managerip(),
                                                 port_=userConfig.get_rabbitmq_rmqport(),
                                                 exchange_=systemConfig.get_rabbitmq_exchange(),
                                                 queue_="{0}_async_{1}".format(systemConfig.get_rabbitmq_listenQueue(),
                                                                               userConfig.get_agent_instanceid()),
                                                 routing_key_="async_{0}".format(userConfig.get_agent_instanceid()))

        self.asyncSender = RabbitMQSender(name_='AsyncResponse', host_=userConfig.get_rabbitmq_managerip(),
                                          port_=userConfig.get_rabbitmq_rmqport(),
                                          exchange_=systemConfig.get_rabbitmq_exchange(),
                                          routing_key_=systemConfig.get_rabbitmq_asyncResponseRouteKey())

        sender = RabbitMQSender(name_='SyncResponse', host_=userConfig.get_rabbitmq_managerip(),
                                port_=userConfig.get_rabbitmq_rmqport(),
                                exchange_=systemConfig.get_rabbitmq_exchange(),
                                routing_key_=systemConfig.get_rabbitmq_responseRouteKey())

        CommandReceiver.__init__(self, context, 'asyncReceiverThread', rabbitMQAsyncReceiver, sender)

    def parseMsg(self, response):
        AgentLog.debug("receive msg: {0}".format(response.body))
        try:
            try:
                command = CommandFactory.getCommand(response.getDBType(), response.getAction())(self.context, response)
            except AttributeError:
                request = self.createErrorRequest(response, 'command is not exist')
                self.sender.send(request.getRequest())
                return

            # 异步消息，需要返回一个响应，表示已经在处理
            self.sender.send(command.responseACK().getRequest())

            data = [((), {'command': command, 'asyncSender': self.asyncSender})]
            reqs = threadpool.makeRequests(doWork, data)
            [AsyncCMDReceiver.pool.putRequest(req) for req in reqs]

        except Exception, e:
            AgentLog.error('AsyncCMDReceiver.parseMsg error %s' % e)
