# -*- coding:UTF-8 -*- 
"""
@author:  hzjianghongxiang
@date:    2015-01-19
@contact: jhx1008@gmail.com
version:  1.0
@todo:
@modify:
"""


class CommandFactory:
    @staticmethod
    def getCommand(dbName, action):
        try:
            url = 'from imagent.'+ dbName+'.commands.'+action+' import '+action
            exec url
            return eval(action)
        except AttributeError,e:
            raise e