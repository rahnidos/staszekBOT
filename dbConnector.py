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

    def select_single(self, q, params=None):
        cur = self.__conn.cursor()
        try:
            if params:
                cur.execute(q, params)
            else:
                cur.execute(q)
        except Exception as e:
            print(f"Database error: {e}")  # Tymczasowo, zamiast loggera
            return False
        r = cur.fetchone()
        cur.close()
        return r[0] if r else False

    def select_list(self, q, params=None):
        cur = self.__conn.cursor()
        try:
            if params:
                cur.execute(q, params)
            else:
                cur.execute(q)
        except Exception as e:
            print(f"Database error: {e}")  # Tymczasowo, zamiast loggera
            return False
        cur.execute(q)
        r = cur.fetchall()
        return r if r else False
    
    def select_random(self, table):
        cur = self.__conn.cursor()
        if table not in {"friends"}:
            return False
        cur.execute("Select * from {table} order by random() limit 1")
        r = cur.fetchone()
        cur.close()
        return r[0] if r else False
    
    def select_random_pic(self, folder):
        cur = self.__conn.cursor()
        cur.execute("Select p.filename, p.folder, f.name "
                    "FROM pics p join folders f "
                    "on p.folder=f.id "
                    "where p.folder=? and p.stat='o' order by random() limit 1",(folder,))
        r = cur.fetchone()
        cur.close()
        return r if r else False
    
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

    