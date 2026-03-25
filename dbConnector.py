from singleton import Singleton
import sqlite3
from dotenv import load_dotenv
import os
@Singleton
class dbConnector(object):

    def __init__(self):
        load_dotenv()
        STASZEKHOME = os.getenv("STASZEKHOME")
        dbpath=os.path.join(STASZEKHOME,'staszek.db')
        self.__conn = sqlite3.connect(dbpath,check_same_thread=False)
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

    def execute(self, q, params=None):
        #@# TODO: błędy wyrzucić do loggera
        cur = self.__conn.cursor()
        try:
            if params:
                cur.execute(q, params)
            else:
                cur.execute(q)
            self.__conn.commit()
        except Exception as e:
            print(f"Database error: {e}")  # Tymczasowo, zamiast loggera
            return False
        cur.close()
        return True

    