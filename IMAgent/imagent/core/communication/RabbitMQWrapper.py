# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-04
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""

import pika

class RabbitMQWrapper:
    def __init__(self, name_="RabbitMQWrapper", host_='localhost', port_=5672, exchange_='exchange', queue_='',
                 routing_key_='key'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host_, port=port_))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange_, exchange_type='direct')
        self.exchange = exchange_
        self.queue = queue_
        self.routing_key = routing_key_
        self.host = host_
        self.port = port_
        self.name = name_
        self.normalExit = False

    def reconnect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, exchange_type='direct')

    def clear(self):
        self.normalExit = True

    def uninit(self):
        self.clear()
        self.connection.close()





