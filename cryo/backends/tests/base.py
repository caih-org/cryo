from __future__ import with_statement

from datetime import datetime
import random

from cryo.session import Session
from cryo.query import Select

from ...tests.testclasses import (CompleteTestClass, TestEnum,
                                  ForeignKeyTestClass,
                                  ForeignKeyTestClassOne,
                                  ForeignKeyTestClassMany)


class BackendTestCase:

    def setUp(self):
        # HACK: this is to suppress pylint errors while coding
        self.connection = None
        self.assertEquals = lambda: True
        self.assertNotEquals = lambda: True
        self.assertTrue = lambda: True
        self.assertFalse = lambda: True
        # end HACK

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

    def test_add_delete(self):
        with Session(self.connection) as session:
            testobj = CompleteTestClass()
            session.append(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))
            self.assertTrue(testobj_query is not None)
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
            testobj.timestamp = datetime.now()
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
