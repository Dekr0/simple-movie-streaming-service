import datetime
import sqlite3
import sys


__database_name = sys.argv[-1]


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class Connection(metaclass=Singleton):

    def __init__(self, name):
        self.__conn = sqlite3.connect(name)

    def commit(self):
        self.__conn.commit()

    def getCursor(self):
        return self.__conn.cursor()


def isValidInt(id):
    if id.isnumeric() and int(id) > 0:
        return True

    return False


def isValidText(text):
    if text != "" and not text.isspace():
        return True

    return False


def isValidYear(year):
    if year.isnumeric() and datetime.MINYEAR <= int(year) <= datetime.datetime.today().year:
        return True

    return False


__conn_wrap = Connection(__database_name)
commit = __conn_wrap.commit
cursor = __conn_wrap.getCursor()
