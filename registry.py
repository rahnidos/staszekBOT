from singleton import Singleton
from dbConnector import dbConnector
import os
from texts import txt
from openaicfg import *

@Singleton
class registry(object):
    cfg={}
    t={}
    aipers=""
    def __init__(self):
        self.sbhome=os.environ.get('STASZEKHOME')
        self.sbdb=os.path.join(os.environ.get('STASZEKHOME'),'staszek.db')
        D = dbConnector.Instance()
        settings=D.select_list("select key,value from settings")
        for setting in settings:
            self.cfg[setting[0]]=setting[1]
        self.t=txt
        self.aipers=personality        
        pass

    def __str__(self):
        return 'Registry object'

    