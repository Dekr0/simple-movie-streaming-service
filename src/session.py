import sqlite3


class Session:

    def __init__(self, sid):
        self.sid = sid
        self.__conn = sqlite3.connect("data.db")
        self.__cursor = self.__conn.cursor()