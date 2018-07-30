'''db封装'''
import pymysql
from config import db_cfg

class Db(object):
    def __init__(self):
        if(db_cfg['engine'] != 'mysql'):
            exit('only mysql engine is ready!')
        self._conn = pymysql.connect(
            host = db_cfg['host'],
            user = db_cfg['username'],
            passwd = db_cfg['passwd'],
            db = db_cfg['database'],
            cursorclass = pymysql.cursors.DictCursor
        )
        self._cursor = self._conn.cursor()

    def __del__(self):
        try:
            self._cursor.close()
            self._conn.close()
        except:
            self._conn.rollback()

    def execute(self, sql='', args=()):
        '''执行非查询sql语句'''
        res = self._cursor.execute(sql, args)
        self._conn.commit()
        return res

    def fetchone(self, sql='', args=()):
        '''查询语句，获取一行'''
        self._cursor.execute(sql, args)
        return self._cursor.fetchone()

    def fetchall(self, sql='', args=()):
        '''查询语句，获取所有'''
        self._cursor.execute(sql, args)
        return self._cursor.fetchall()

db = Db()











