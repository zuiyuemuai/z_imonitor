#coding=utf-8


class MonitorFilter(object):
    def __init__(self, attr):
        self.attr = attr

    def filter(self, data):
        return data


class ReplaceFilter(MonitorFilter):
    def __init__(self, attr):
        MonitorFilter.__init__(self, attr)
        self.replace_dict = attr

    def doReplace(self, infos):
        for (key, value) in self.replace_dict.items():
            keys = key.split('.')
            temp = infos
            for key in keys[:-1]:
                temp = temp.get(key, None)
                if temp == None:
                    break  # modified by luqianjie for 原来是return，这样如果替换配置一项写错会导致其他配置项也不能用，这里变为break
            if not temp == None:  # 如果不为None则进行替换
                data = temp.pop(keys[-1])
                for v in value:
                    temp[v] = data

    def filter(self, data):
        self.doReplace(data)
        return data


class IgnoreFilter(MonitorFilter):
    def __init__(self, attr):
        MonitorFilter.__init__(self,attr)
        self.ignore_list = attr

    def doIgnore(self, infos):
        for item in self.ignore_list:
            keys = item.split('.')
            length = len(keys)
            d = infos
            for i in xrange(0, length - 1):
                if d.has_key(keys[i]):
                    d = d[keys[i]]
                else:
                    d = {}
                    break
            if d.has_key(keys[length - 1]):
                d.pop(keys[length - 1])

    def filter(self, data):
        self.doIgnore(data)
        return data
