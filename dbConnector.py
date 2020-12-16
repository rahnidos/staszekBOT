from singleton import Singleton
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
    def getRandomAnswer(self,quest):
        q = "select answer from answers where question='%s' ORDER BY RANDOM() LIMIT 1;" % (quest)
        ret = self.select_single(q)
        return ret
    def getRolls(self):
        q = "select thing, func from rolls"
        list = self.select_list(q)
        ret={}
        for row in list:
            ret[row[0]]=row[1]
        return ret
    def getRandomSticker(self,tag):
        q = "select fileid from stickers where tag LIKE '%s' ORDER BY RANDOM() LIMIT 1;" % ('%'+tag+'%')
        ret=self.select_single(q)
        return ret
    def insertChannel(self, chid, chname):
        q = "insert into channel (id, name) values('%s','%s')" % (chid, chname)
        ret= self.execute(q)
        return ret
    def insertFriend(self, user, chid):
        q = "insert into friends (user, chid) values (%d,'%s') on conflict(user,chid) do nothing" % (user,chid)
        ret=self.execute(q)
        return ret
    def getRandomFriend(self, chid):
        q = "select user from friends where chid='%s' order by random() limit 1;" % (chid)
        ret=self.select_single(q)
        return ret
    def removeFriend(self, user, chid):
        q = "delete from friends where chid='%s' and user =%d" % (str(chid), user)
        ret=self.execute(q)
        return ret
    def addSticker(self, sid, tag):
        q = "insert into stickers (fileid,tag) values('%s','%s')" %(sid,tag)
        ret=self.execute(q)
        return ret
    def getFriendlyChannels(self,uid):
        q = "select chid, name from friends join channel on friends.chid=channel.id where friends.user=%d" % (uid)
        ret=self.select_list(q)
        return ret
    def addAnswer(self,question,answer):
        q = "insert into answers (id,answer,question) values((select max(id) from answers)+1,'%s','%s')" % (answer,question)
        ret=self.execute(q)
        return ret
    def addRollSticker(self,comm,alias):
        q = "insert into rolls (thing,func) values('%s','%s')" %(alias,comm)
        ret=self.execute(q)
        return ret
    def getAreas(self,tag=''):
        if tag:
            q="select minlat,maxlat,minlong,maxlong,w,INSTR(name, '%s') tag  from areas where tag>0"% (tag)
        else:
            q="select minlat,maxlat,minlong,maxlong,w from areas"
        ret=self.select_list(q)
        return ret
