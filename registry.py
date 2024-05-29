from singleton import Singleton
from dbConnector import dbConnector
import os

@Singleton
class registry(object):
    def __init__(self):
        self.sbhome=os.environ.get('STASZEKHOME')
        self.sbdb=os.path.join(os.environ.get('STASZEKHOME'),'staszek.db')
        D = dbConnector.Instance()
        self.token=D.select_single("select value from settings where key='token'")
        self.ownerId=D.select_single("select value from settings where key='owner'")
        pass

    def __str__(self):
        return 'Registry object'

    