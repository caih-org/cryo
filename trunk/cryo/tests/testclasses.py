#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2008  César Izurieta

This file is part of Cryo.

Cryo is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__author__ = "César Izurieta"
__email__ = "cesar at caih dot org"
__version__ = "$Revision$"[11:-2]

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
