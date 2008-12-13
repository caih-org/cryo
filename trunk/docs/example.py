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

from __future__ import with_statement

__author__ = "César Izurieta"
__email__ = "cesar at caih dot org"
__version__ = "$Revision$"[11:-2]

from datetime import datetime

from enum import Enum

from cryo.session import Session
from cryo.metadata import Table, Column
from cryo.datatypes import Text, One, Many
from cryo.backends.sqlite import SQLiteBackend
from cryo.query import Select, Field

class A:

    def __init__(self, name="", description=""):
        self.name = name
        self.description = description
        self.excluded = None


class B:

    def __init__(self, name="", a=None, status1="", status2=""):
        self.name = name
        self.a = a
        self.cs = list()
        self.status1 = status1
        self.status2 = status2

someenum = Enum('a', 'b', 'c')

class C:

    def __init__(self, name=""):
        self.name = name
        self.excluded = True
        self.boolean = False
        self.integer = 1
        self.decimal = 1.1
        self.long = 1L
        self.datetime = datetime.now()
        self.enum = someenum.a


class D:

    def __init__(self, name=""):
        self.name = name
        self.a = None
        self.bs = []


def main():
    test(init())


def init():
    connection = SQLiteBackend("example.sqlite", modules=[__import__(__name__)]).newconnection()

    #########################
    # A
    a_table = Table(A, primarykey=('name',))

    #########################
    # B
    b_table = Table(B,
                    attributes={'name': Column('b_name', Text(2)),
                                'a': One(A),
                                'cs': Many(C),
                                'status1': str,
                                'status2': ""},
                    primarykey=('name', 'a'))

    #########################
    # C
    c_table = Table(C, name='table_c', attributes={'excluded': None},
                    primarykey=('name',))

    #########################
    # D
    d = D()
    d.a = A()
    d.bs = [B()]
    d_table = Table(D, example=d, primarykey=('name', ))
    d_table.columns['name'].name = 'd_name'

    #########################
    # CREATE TABLES
    connection.setup(a_table, b_table, c_table, d_table)

    return connection


def test(connection):
    with Session(connection) as session:
        a1 = A("a1", "one")
        a2 = A("a2", "two")

        assert a1 not in session
        assert a2 not in session

        a3_1 = A("a3", "three A")
        a3_2 = A("a3", "three B")

        assert session.same(a3_1, a3_2)

        session.append(a1)
        session.append(a2)
        session.append(a3_1)
        session.append(a3_2)

        assert a1 in session
        assert a2 in session
        
        del session[a3_1]

        assert a1 in session
        assert a2 in session
        assert a3_1 not in session
        assert a3_2 not in session

        b1 = B("b1", a1, "ok", "good")

        session.append(b1)

    with Session(connection) as session:
        a = session.queryone(Select(A).where(Field("name"), "LIKE", "a1")
                             .orderby('name'))

        objsB = session.query(Select(B))
        for obj in objsB:
            assert session.same(a, obj.a)


    with Session(connection) as session:
        for n in range(12500):
            session.append(A("a%i" % n, "generated"))

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

    main()
