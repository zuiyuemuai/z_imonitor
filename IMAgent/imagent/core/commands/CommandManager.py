__author__ = 'lynn'
from imagent.core.application.Manager import Manager
from imagent.core.commands.SyncCMDReceiver import SyncCMDReceiver
from imagent.core.commands.AsyncCMDReceiver import AsyncCMDReceiver

class CommandManager(Manager):

    def __init__(self,context):
        Manager.__init__(self, 'CommandManager')
        self.context = context
        uConfig = context.userConfig
        sConfig = context.systemConfig
        self.rabbitMQWrappers = []
        self.receivers = []
        self.receivers.append(SyncCMDReceiver(context))
        self.receivers.append(AsyncCMDReceiver(context))


    def start(self):
        for receiver in self.receivers:
            receiver.start()

    def stop(self):
        for receiver in self.receivers:
            receiver.stop()



