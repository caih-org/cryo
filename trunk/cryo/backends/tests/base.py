from __future__ import with_statement

from datetime import datetime
import random

from cryo.session import Session
from cryo.query import (Select, Field, WhereClause, CompareWhereClause,
                        AndWhereClause, OrWhereClause)

from ...tests.testclasses import (CompleteTestClass, TestEnum,
                                  ForeignKeyTestClass,
                                  ForeignKeyTestClassOne,
                                  ForeignKeyTestClassMany)


class BackendTestCaseMixin:

    ##########################
    # SESSION

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

    ##########################
    # DB TRANSACTIONS

    def test_add_delete(self):
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

    ##########################
    # DATATYPES

    def test_datatypes_excluded(self):
        testobj = CompleteTestClass()
        with Session(self.connection) as session:
            testobj.excluded = 'excluded'
            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))
            self.assertNotEquals(testobj.excluded, testobj_query)

    def test_datatypes_default(self):
        testobj = CompleteTestClass()
        with Session(self.connection) as session:
            testobj.excluded = 'excluded'
            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))
            for attr in ['name', 'boolean', 'text', 'longtext',
                         'integer', 'decimal', 'long', 'timestamp',
                         'pythonobject']:
                self.assertEquals(getattr(testobj, attr),
                                  getattr(testobj_query, attr))
            self.assertEquals(testobj.enum.index, testobj_query.enum.index)

    def test_datatypes(self):
        testobj = CompleteTestClass()
        with Session(self.connection) as session:
            testobj.name = 'test'
            testobj.boolean = not testobj.boolean
            testobj.enum = TestEnum.second
            testobj.text = "text_" + str(random.randint(1, 20))
            testobj.longtext = "y" * 1000
            testobj.integer = 2
            testobj.decimal = 3.0
            testobj.long = 4L
            testobj.timestamp = datetime(10, 10, 10)
            testobj.pythonobject = True
            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))
            for attr in ['name', 'boolean', 'text', 'longtext',
                         'integer', 'decimal', 'long', 'timestamp',
                         'pythonobject']:
                self.assertEquals(getattr(testobj, attr),
                                  getattr(testobj_query, attr))
            self.assertEquals(testobj.enum.index, testobj_query.enum.index)

    ##########################
    # FOREIGN KEYS

    def test_foreignkeys_one_none(self):
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

    def test_foreignkeys_one_add_delete(self):
        with Session(self.connection) as session:
            testobj = ForeignKeyTestClass('a')
            session.append(testobj)

            self.assertTrue(testobj in session)
            self.assertTrue(testobj.one not in session)
            self.assertEquals(len(session), 1)

            session.commit()

            self.assertTrue(testobj in session)
            self.assertTrue(testobj.one in session)
            self.assertEquals(len(session), 2)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(ForeignKeyTestClass))
            self.assertTrue(testobj_query is not None)
            self.assertEquals(len(session), 2)
            del session[testobj_query]

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(ForeignKeyTestClass))
            self.assertTrue(testobj_query is None)

            testobj_query = session.queryone(Select(ForeignKeyTestClassOne))
            self.assertTrue(testobj_query is not None)

    def test_foreignkeys_many_add_delete(self):
        with Session(self.connection) as session:
            testobj = ForeignKeyTestClass('a')
            testobj.one = None
            testobjmany_1 = ForeignKeyTestClassMany('c', testobj)
            testobjmany_2 = ForeignKeyTestClassMany('d', testobj)

            testobj.many = [testobjmany_1, testobjmany_2]

            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(ForeignKeyTestClass))
            self.assertTrue(testobj_query is not None)
            self.assertEquals(len(session), 1)
            del session[testobj_query]

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(ForeignKeyTestClass))
            self.assertTrue(testobj_query is None)

            testobj_query = session.queryone(Select(ForeignKeyTestClassOne))
            self.assertTrue(testobj_query is not None)


    ##########################
    # QUERIES

    def test_get(self):
        hashkey = None
        with Session(self.connection) as session:
            testobj = CompleteTestClass()
            session.append(testobj)
            hashkey = session.gethashkey(testobj)

        with Session(self.connection) as session:
            testobj_query = session.get(CompleteTestClass, hashkey)
            self.assertTrue(testobj_query is not None)

    def _fill_for_query(self):
        with Session(self.connection) as session:
            for a in range(10):
                testobj = CompleteTestClass(str(a))
                session.append(testobj)

    def test_query_where_full(self):
        self._fill_for_query()

        with Session(self.connection) as session:
            results = list(session.query(Select(CompleteTestClass)))

            self.assertEquals(len(results), 10)

    def test_query_where_field(self):
        self._fill_for_query()

        with Session(self.connection) as session:
            results = list(session.query(Select(CompleteTestClass)
                                         .where(Field('name') == 5)))

            self.assertEquals(len(results), 1)

            results = list(session.query(Select(CompleteTestClass)
                                         .where(5 == Field('name'))))

            self.assertEquals(len(results), 1)

            results = list(session.query(Select(CompleteTestClass)
                                         .where(Field('name') ==
                                                Field('name'))))

            self.assertEquals(len(results), 10)

            results = list(session.query(Select(CompleteTestClass)
                                         .where(1, '=', 2)))

            self.assertEquals(len(results), 0)

    def test_query_field(self):
        self.assertTrue(isinstance(Field('a') == 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') != 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') > 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') >= 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') < 0, CompareWhereClause))
        self.assertTrue(isinstance(Field('a') <= 0, CompareWhereClause))

        self.assertTrue(isinstance(0 == Field('a'), CompareWhereClause))

        self.assertTrue(isinstance(Field('a') == Field('b'),
                                   CompareWhereClause))

    def test_query_whereclause(self):
        query = (Field('a') == 0) & (Field('b') == 1)
        self.assertTrue(isinstance(query, AndWhereClause))

        query = (Field('a') == 0) | (Field('b') == 1)
        self.assertTrue(isinstance(query, OrWhereClause))

    def test_query_where_or(self):
        self._fill_for_query()

        with Session(self.connection) as session:
            where = (Field('name') == 1) | (Field('name') == 2)
            results = list(session.query(Select(CompleteTestClass)
                                         .where(where)))

            self.assertEquals(len(results), 2)

    def test_query_where_and(self):
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
