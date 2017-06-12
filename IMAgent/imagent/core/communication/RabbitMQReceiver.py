# -*- coding:UTF-8 -*-

from pika.exceptions import ConnectionClosed

from imagent.core.common.AgentLog import AgentLog
from RabbitMQWrapper import RabbitMQWrapper
from AgentResponse import AgentResponse


class RabbitMQReceiver(RabbitMQWrapper):
    def __init__(self, name_='RabbitMQReceiver', host_='localhost', port_=5672, exchange_='exchange', queue_='',
                 routing_key_='key'):
        RabbitMQWrapper.__init__(self, name_, host_, port_, exchange_, queue_, routing_key_)
        self.exclusive = False
        if queue_ == "":
            queue_ = self.channel.queue_declare(exclusive=True).method.queue
            self.queue = queue_
            self.exclusive = True
        else:
            self.channel.queue_declare(queue=queue_)
        self.channel.queue_bind(exchange=exchange_, queue=queue_, routing_key=routing_key_)
        self.doWork = None
        AgentLog.info("create receiver %s {host:%s, port:%d, exchange:%s, routing_key:%s}" % (
        name_, host_, port_, exchange_, routing_key_))

    def reconnect(self):
        AgentLog.warning("receiver %s disconnectted, re-connect..." % self.name)
        RabbitMQWrapper.reconnect(self)
        queue_ = self.queue
        if self.exclusive:
            queue_ = self.channel.queue_declare(exclusive=True).method.queue
            self.queue = queue_
        else:
            self.channel.queue_declare(queue=queue_)
        self.channel.queue_bind(exchange=self.exchange, queue=queue_, routing_key=self.routing_key)

    def callback(self, ch, method, properties, body):
        try:
            self.doWork(AgentResponse(body))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception,e:
            AgentLog.error('RabbitMQReceiver.callback error %s'%e)

    def receive(self, doWork, ack=False):
        self.doWork = doWork
        while 1:
            try:
                self.channel.basic_consume(self.callback, queue=self.queue, no_ack=ack)
                self.channel.start_consuming()
            except KeyboardInterrupt:
                AgentLog.warning("receive KeyboardInterrupt error")
                break
            except ConnectionClosed, e:
                AgentLog.warning("receive ConnectionClosed error:%s" % e)
                if not self.normalExit:
                    self.reconnect()
                else:
                    break
            except Exception, e:
                self.reconnect()
                AgentLog.warning("receive error: %s" % e)
            except:
                self.reconnect()
                AgentLog.warning("receive failed, unknown errors")

    def clear(self):
        RabbitMQWrapper.clear(self)
        self.channel.stop_consuming()

