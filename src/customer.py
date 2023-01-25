import sqlite3


class Customer:

    def __init__(self, cid):
        self.cid = cid
        self.__conn = sqlite3.connect("data.db")
        self.__cursor = self.__conn.cursor()

    def handle(self):
        # while(True):
        #     pass
        pass

    def startSession(self):
        pass

    def searchMovie(self):
        pass

    def endSession(self):
        pass