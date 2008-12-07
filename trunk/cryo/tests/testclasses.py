from datetime import datetime
from enum import Enum

from cryo.metadata import Table
from cryo.datatypes import One, Many, PythonObject

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

    def __init__(self, name=''):
        self.name = name
        self.one = ForeignKeyTestClassOne(foreignkeytest=self)
        self.many = []
        self.many_autofetch = []


class ForeignKeyTestClassOne:

    def __init__(self, name='', foreignkeytest=None):
        self.name = name
        self.one = foreignkeytest or ForeignKeyTestClass()


class ForeignKeyTestClassMany:

    def __init__(self, name='', foreignkeytest=None):
        self.name = name
        self.one = foreignkeytest or ForeignKeyTestClass()
        self.one_autofetch = foreignkeytest or ForeignKeyTestClass()


def gettables():
    return [Table(CompleteTestClass,
                  primarykey=('name',),
                  attributes={'pythonobject': PythonObject()}),
            Table(ForeignKeyTestClass,
                  primarykey=('name',),
                  attributes={'one': One(ForeignKeyTestClassOne),
                              'many': Many(ForeignKeyTestClassMany),
                              'many_autofetch': Many(ForeignKeyTestClassMany,
                                                     autofetch=True)}),
            Table(ForeignKeyTestClassOne,
                  primarykey=('name',),
                  attributes={'one': One(ForeignKeyTestClass, inverse='one')}),
            Table(ForeignKeyTestClassMany,
                  primarykey=('name',),
                  attributes={'one': One(ForeignKeyTestClass, inverse='many'),
                              'one_autofetch': One(ForeignKeyTestClass,
                                                   inverse='many_autofetch')})]
