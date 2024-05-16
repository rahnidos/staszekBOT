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

    