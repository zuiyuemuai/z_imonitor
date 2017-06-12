# -*- coding:UTF-8 -*-

from pika.exceptions import ConnectionClosed

from imagent.core.common.AgentLog import AgentLog
from RabbitMQWrapper import RabbitMQWrapper


class RabbitMQSender(RabbitMQWrapper):
    def __init__(self, name_="RabbitMQSender", host_="localhost", port_=5672, exchange_='exchange', routing_key_='key'):
        RabbitMQWrapper.__init__(self, name_, host_, port_, exchange_, '', routing_key_)
        AgentLog.info("create sender %s {host:%s, port:%d, exchange:%s, routing_key:%s}" % (
        name_, host_, port_, exchange_, routing_key_))

    def send(self, msg):
        try:
            self.channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=msg)
        except ConnectionClosed, e:
            self.reconnect()
            self.channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=msg)
        except Exception, e:
            AgentLog.error("{0} send msg:{1} error".format(self.name, msg))
        if len(msg) > 128:
            AgentLog.debug("{0} send msg: {1}".format(self.name, msg[:128]))
        else:
            AgentLog.debug("{0} send msg: {1}".format(self.name, msg))