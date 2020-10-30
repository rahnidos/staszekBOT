from singleton import Singleton
#from staszek imort staszek
import sqlite3
import os
@Singleton
class dbConnector(object):

    def __init__(self):
        hpath=os.environ.get('STASZEKHOME')
        self.__conn = sqlite3.connect(hpath+'staszek.db',check_same_thread=False)
        pass

    def __str__(self):
        return 'Database connection object'

    def select_single(self, q):
        cur = self.__conn.cursor()
        cur.execute(q)
        r = cur.fetchone()
        cur.close()
        if r: return r[0]
        else: return False

    def select_list(self, q):
        cur = self.__conn.cursor()
        cur.execute(q)
        r = cur.fetchall()
        if r: return r
        else: return False

    def execute(self, q):
        #@# TODO: błędy wyrzucić do loggera
        cur = self.__conn.cursor()
        try:
            cur.execute(q)
            self.__conn.commit()
        except:
            return False
        cur.close()
        return True

    def getParam(self, key):
        q = "select value from settings where key='%s'" % (key)
        ret = self.select_single(q)
        return ret
    def setParam(self, key, value):
        q = "insert into settings (key,value) values('%s','%s')" % (key,value)
        return self.execute(q)
    def delParam(self, key):
        q = "delete from settings where key='%s'" % (key)
        return self.execute(q)
    def updateParam(self, key, value):
        q = "update settings set value = '%s' where key = '%s'" % (value,key)
        return self.execute(q)

    def getCommand(self, alias):
        q = "select value from commands where alias='%s'" % (alias)
        ret = self.select_single(q)
        return ret
    def getCommands(self):
        q = "select alias, real, type from commands order by type"
        ret = self.select_list(q)
        return ret
    def getRandomAnswer(self):
        q = "select answer from answers where question='%s' ORDER BY RANDOM() LIMIT 1;" % (q)
        ret = self.select_single(q)
        return ret
    def getRolls(self):
        q = "select thing, func from rolls"
        list = self.select_list(q)
        ret={}
        for row in list:
            ret[row[0]]=row[1]
        return ret
