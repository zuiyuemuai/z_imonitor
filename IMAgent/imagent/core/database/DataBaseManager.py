#coding=utf-8
from imagent.core.common.AgentException import AgentException
from imagent.core.common.AgentFileException import AgentFileException

class DataBaseManager(object):
    @staticmethod
    def createDataBase(name, attr):
        try:
            url = 'from imagent.'+ name+'.'+name+' import '+name
            exec url
            return eval(name)(attr)
        except KeyError,e:
            raise AgentException('DataBaseManager.createDataBase KeyError:%s'%e)
        except AttributeError,e:
            # AgentLog.error('DataBaseManager.createDataBase config name is error value: %s'%dbConfig['name'])
            raise AgentException('DataBaseManager.createDataBase config name is error value: %s'%name)
        except TypeError,e:
            # AgentLog.error('DataBaseManager.createDataBase config attar is error value: %s'%dbConfig['attr'])
            raise AgentException('DataBaseManager.createDataBase config attar is error value: %s'%attr)
        except AgentFileException,e:
            raise AgentException('DataBaseManager.createDataBase error: %s'%e)