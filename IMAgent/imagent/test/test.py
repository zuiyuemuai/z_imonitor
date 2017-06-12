__author__ = 'hzluqianjie'

import imagent

#eval('from imagent import conf')
#eval('1+1')
from imagent.conf.setting import INSTALL_APPS
# list = INSTALL_APPS[0].split('.')

# getattr(imagent,'mysql')
module = __import__(INSTALL_APPS[0])