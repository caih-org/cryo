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
import random
import math

from cryo.session import Session
from cryo.query import (Select, Field, CompareWhereClause,
                        AndWhereClause, OrWhereClause)

from ...tests import testclasses
from ...tests.testclasses import (CompleteTestClass, TestEnum,
                                  ForeignKeyTestClass,
                                  ForeignKeyTestClassOne,
                                  ForeignKeyTestClassMany)


class SessionTestCaseMixin:

    def test_session_empty(self):
        with Session(self.connection) as session:
            self.assertEquals(len(session), 0)

            testobj = CompleteTestClass()
            session.append(testobj)

        with Session(self.connection) as session:
            self.assertEquals(len(session), 0)

    def test_session_add(self):
        with Session(self.connection) as session:
            testobj = CompleteTestClass()

            self.assertTrue(testobj not in session)

            session.append(testobj)
    
            self.assertTrue(testobj in session)
            self.assertEquals(len(session), 1)

    def test_session_same(self):
        with Session(self.connection) as session:
            testobj_1 = CompleteTestClass()
            testobj_2 = CompleteTestClass()

            self.assertTrue(session.same(testobj_1, testobj_2))

            session.append(testobj_1)
            session.append(testobj_2)

            self.assertTrue(testobj_1 not in session)
            self.assertTrue(testobj_2 in session)

    def test_session_same_delete_other(self):
        with Session(self.connection) as session:
            testobj_1 = CompleteTestClass()
            testobj_2 = CompleteTestClass()

            session.append(testobj_2)

            self.assertTrue(testobj_1 not in session)
            self.assertTrue(testobj_2 in session)

            del session[testobj_1]

            self.assertTrue(testobj_1 not in session)
            self.assertTrue(testobj_2 not in session)

    def test_session_not_same(self):
        with Session(self.connection) as session:
            testobj1 = CompleteTestClass('1')
            testobj2 = CompleteTestClass('2')

            self.assertFalse(session.same(testobj1, testobj2))


class TransactionsTestCaseMixin:

    def test_add_delete_commit(self):
        with Session(self.connection) as session:
            testobj = CompleteTestClass()
            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))
            self.assertTrue(testobj_query is not None)
            self.assertTrue(testobj_query in session)
            del session[testobj_query]

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))
            self.assertTrue(testobj_query is None)

    def test_rollback(self):
        testobj = CompleteTestClass()
        with Session(self.connection) as session:
            session.append(testobj)
            session.rollback()
            self.assertTrue(testobj not in session)

        with Session(self.connection) as session:
            session.append(testobj)
            session.commit()
            del session[testobj]
            session.rollback()
            self.assertTrue(testobj in session)


class DatatypesTestCaseMixin:

    def _test_datatype(self, attr, value1, value2):
        testobj = CompleteTestClass()

        with Session(self.connection) as session:
            setattr(testobj, attr, value1)
            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))

            self.assertEquals(getattr(testobj_query, attr), value1)
            self.assertNotEquals(getattr(testobj_query, attr), value2)

            setattr(testobj_query, attr, value2)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))

            self.assertEquals(getattr(testobj_query, attr), value2)
            self.assertNotEquals(getattr(testobj_query, attr), value1)

    def test_boolean(self):
        self._test_datatype('boolean', True, False)

    def test_enum(self):
        self._test_datatype('enum', TestEnum.first, TestEnum.second)

    def test_text(self):
        self._test_datatype('text', 'text_1_' + str(random.randint(1, 20)),
                            'text_2_' + str(random.randint(1, 20)))

    def test_longetext(self):
        self._test_datatype('longtext', 'y' * 1000, 'z' * 1000)

    def test_number_integer(self):
        self._test_datatype('integer', 12345, -67890)

    def test_number_decimal(self):
        self._test_datatype('decimal', 1.1, math.pi)

    def test_number_long(self):
        self._test_datatype('long', 1L, 1234567890L)

    def test_timestamp(self):
        self._test_datatype('timestamp', datetime(1983, 3, 1),
                            datetime(10, 10, 10))

    def test_pythonobject(self):
        # FIXME: find better examples for python objects
        self._test_datatype('pythonobject', True, datetime.now())

    def test_datatypes_excluded(self):
        testobj = CompleteTestClass()

        with Session(self.connection) as session:
            testobj.excluded = 'excluded'
            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))

            self.assertNotEquals(testobj.excluded, testobj_query.excluded)

    def test_datatypes_default(self):
        testobj = CompleteTestClass()

        with Session(self.connection) as session:
            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))

            for attr in ['name', 'boolean', 'enum', 'text', 'longtext',
                         'integer', 'decimal', 'long', 'timestamp',
                         'pythonobject']:
                self.assertEquals(getattr(testobj, attr),
                                  getattr(testobj_query, attr))


class ForeignKeyTestCaseMixin:

    def test_foreignkey_one_none(self):
        with Session(self.connection) as session:
            testobj = ForeignKeyTestClass('a')
            testobj.one = None
            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(ForeignKeyTestClass))

            self.assertTrue(testobj_query is not None)
            self.assertTrue(testobj_query.one is None)
            self.assertEquals(len(session), 1)

            testobjone_query = session.queryone(Select(ForeignKeyTestClassOne))

            self.assertTrue(testobjone_query is None)
            self.assertEquals(len(session), 1)

    def test_foreignkey_one_add_delete(self):
        with Session(self.connection) as session:
            testobj = ForeignKeyTestClass('a')
            session.append(testobj)

            self.assertTrue(testobj in session)
            self.assertTrue(testobj.one not in session)
            self.assertEquals(len(session), 1)

            session.append(testobj.one)

            self.assertTrue(testobj in session)
            self.assertTrue(testobj.one in session)
            self.assertEquals(len(session), 2)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(ForeignKeyTestClass))

            self.assertTrue(testobj_query is not None)
            self.assertTrue(testobj_query.one is not None)
            self.assertEquals(len(session), 2)

            del session[testobj_query]

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(ForeignKeyTestClass))

            self.assertTrue(testobj_query is None)

            testobj_query = session.queryone(Select(ForeignKeyTestClassOne))

            self.assertTrue(testobj_query is not None)

    def test_foreignkey_many_add_delete(self):
        with Session(self.connection) as session:
            testobj = ForeignKeyTestClass('a')
            testobj.one = None
            testobj.many = [ForeignKeyTestClassMany('c', testobj),
                            ForeignKeyTestClassMany('d', testobj)]

            session.append(testobj)
            session.append(testobj.many)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(ForeignKeyTestClass))

            self.assertTrue(testobj_query is not None)
            self.assertEquals(len(session), 1)

            del session[testobj_query]

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(ForeignKeyTestClass))
            self.assertTrue(testobj_query is None)

            results = session.query(Select(ForeignKeyTestClassMany))
            self.assertEquals(len(list(results)), 2)


class QueryTestCaseMixin:

    def _fill_for_query(self):
        with Session(self.connection) as session:
            for a in range(10):
                testobj = CompleteTestClass(str(a))
                session.append(testobj)

    def test_get(self):
        hashkey = None

        with Session(self.connection) as session:
            testobj = CompleteTestClass()
            session.append(testobj)
            hashkey = session.gethashkey(testobj)

        with Session(self.connection) as session:
            testobj_query = session.get(CompleteTestClass, hashkey)
            self.assertTrue(testobj_query is not None)

    def test_query_where_full(self):
        self._fill_for_query()

        with Session(self.connection) as session:
            results = list(session.query(Select(CompleteTestClass)))

            self.assertEquals(len(results), 10)

    def test_field(self):
        # Basic comparisons
        self.assertTrue(isinstance(Field('a') == 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') != 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') > 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') >= 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') < 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') <= 0, CompareWhereClause))

        # The inverse should work too
        self.assertTrue(isinstance(0 == Field('a'), CompareWhereClause))

        # Test with two fields
        self.assertTrue(isinstance(Field('a') == Field('b'),
                                   CompareWhereClause))

    def test_query_fieldcomparison(self):
        self._fill_for_query()

        with Session(self.connection) as session:
            results = session.query(Select(CompleteTestClass)
                                    .where(Field('name') == 5))

            self.assertEquals(len(list(results)), 1)

            results = session.query(Select(CompleteTestClass)
                                    .where(5 == Field('name')))

            self.assertEquals(len(list(results)), 1)

            results = session.query(Select(CompleteTestClass)
                                    .where(Field('name') == Field('name')))

            self.assertEquals(len(list(results)), 10)

            results = session.query(Select(CompleteTestClass).where(1, '=', 2))

            self.assertEquals(len(list(results)), 0)

    def test_query_where(self):
        query = (Field('a') == 0) & (Field('b') == 1)
        self.assertTrue(isinstance(query, AndWhereClause))

        query = (Field('a') == 0) | (Field('b') == 1)
        self.assertTrue(isinstance(query, OrWhereClause))

    def test_query_or(self):
        self._fill_for_query()

        with Session(self.connection) as session:
            where = (Field('name') == 1) | (Field('name') == 2)
            results = list(session.query(Select(CompleteTestClass)
                                         .where(where)))

            self.assertEquals(len(results), 2)

    def test_query_and(self):
        self._fill_for_query()

        with Session(self.connection) as session:
            where = (Field('name') != 7) & (Field('name') > 5)
            results = list(session.query(Select(CompleteTestClass)
                                         .where(where)))

            self.assertEquals(len(results), 3)

            where = (Field('name') == 7) & (Field('name') > 5)
            results = list(session.query(Select(CompleteTestClass)
                                         .where(where)))

            self.assertEquals(len(results), 1)

    def test_query_limit(self):
        self._fill_for_query()

        with Session(self.connection) as session:
            results = list(session.query(Select(CompleteTestClass)[2:5]))

            self.assertEquals(len(results), 3)

    def test_query_orderby(self):
        self._fill_for_query()

        with Session(self.connection) as session:
            results = list(session.query(Select(CompleteTestClass)
                                         .orderby('name')))

            self.assertEquals(len(results), 10)
            for a in range(10):
                self.assertEquals(results[a].name, str(a))


class BackendTestCaseMixin(#SessionTestCaseMixin, TransactionsTestCaseMixin,
                           #DatatypesTestCaseMixin, ForeignKeyTestCaseMixin,
                           #QueryTestCaseMixin):
                           DatatypesTestCaseMixin):

    def _setUp(self, backend):
        self.backend = backend
        self.connection = self.backend.newconnection()
        self.connection.setup(testclasses.gettables())

    def test_rerunsetup(self):
        self.connection.setup(testclasses.gettables())

