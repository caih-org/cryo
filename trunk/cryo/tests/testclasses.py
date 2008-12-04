from datetime import datetime
from enum import Enum

from cryo.metadata import Table, Column
from cryo.datatypes import Text, One, Many, PythonObject

TestEnum = Enum('first', 'second', 'third')


class PythonObjectTest():

    def __init__(self):
        self.name = ""

    def __eq__(self, other):
        return self.name == other.name


class CompleteTestClass:

    def __init__(self, name=""):
        self.name = name
        self.boolean = False
        self.enum = TestEnum.first
        self.text = "short"
        self.longtext = "x" * 1000
        self.integer = 1
        self.decimal = 1.1
        self.long = 1L
        self.timestamp = datetime.now()
        self.pythonobject = PythonObjectTest()
        self.excluded = None


class ForeignKeyTestClass:

    def __init__(self):
        self.name = ""
        self.one = ForeignKeyTestClassOne(self)
        self.many = []


class ForeignKeyTestClassOne:

    def __init__(self, foreignkeytest=None):
        self.name = ""
        self.one = foreignkeytest or ForeignKeyTestClass()


class ForeignKeyTestClassMany:

    def __init__(self, foreignkeytest=None):
        self.name = ""
        self.one = foreignkeytest or ForeignKeyTestClass()


def gettables():
    return [Table(CompleteTestClass,
                  primarykey=('name',),
                  attributes={'pythonobject': PythonObject()}),
            Table(ForeignKeyTestClass,
                  primarykey=('name',),
                  attributes={'one': One(ForeignKeyTestClassOne),
                              'many': Many(ForeignKeyTestClassMany)}),
            Table(ForeignKeyTestClassOne,
                  primarykey=('name',),
                  attributes={'one': One(ForeignKeyTestClass, inverse=True)}),
            Table(ForeignKeyTestClassMany,
                  primarykey=('name',),
                  attributes={'one': One(ForeignKeyTestClass, inverse=True)})]
