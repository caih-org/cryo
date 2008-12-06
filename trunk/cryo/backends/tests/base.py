from __future__ import with_statement

from datetime import datetime
import random

from cryo.session import Session
from cryo.query import Select

from ...tests.testclasses import CompleteTestClass, TestEnum
from ... import util

class BackendTestCase():

    def setUp(self, connection):
        self.connection = connection

    def test_session(self):
        with Session(self.connection) as session:
            self.assertEquals(len(session), 0)

            testobj1 = CompleteTestClass("1")
            testobj2 = CompleteTestClass("2")
    
            self.assertTrue(testobj1 not in session)
            self.assertTrue(testobj2 not in session)
    
            testobj3_1 = CompleteTestClass("3")
            testobj3_2 = CompleteTestClass("3")
    
            self.assertTrue(session.same(testobj3_1, testobj3_2))
    
            session.add(testobj1)
            session.add(testobj2)
            session.add(testobj3_1)
            session.add(testobj3_2)
    
            self.assertTrue(testobj1 in session)
            self.assertTrue(testobj2 in session)
            self.assertTrue(testobj3_1 in session)
            self.assertTrue(testobj3_2 in session)
            self.assertEquals(len(session), 3)

            del session[testobj3_1]

            self.assertTrue(testobj1 in session)
            self.assertTrue(testobj2 in session)
            self.assertTrue(testobj3_1 not in session)
            self.assertTrue(testobj3_2 not in session)
            self.assertEquals(len(session), 2)

        with Session(self.connection) as session:
            self.assertEquals(len(session), 0)

    def test_add_delete(self):
        with Session(self.connection) as session:
            testobj = CompleteTestClass()
            session.add(testobj)

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
            session.add(testobj)
            session.rollback()
            self.assertTrue(testobj in session)

        with Session(self.connection) as session:
            session.add(testobj)
            session.commit()
            del session[testobj]
            session.rollback()
            self.assertTrue(testobj in session)

    def test_datatypes_excluded(self):
        testobj = CompleteTestClass()
        with Session(self.connection) as session:
            testobj.excluded = 'excluded'
            session.add(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))
            for attr in ['name', 'boolean', 'enum', 'text', 'longtext',
                         'integer', 'decimal', 'long', 'timestamp',
                         'pythonobject']:
                self.assertEquals(getattr(testobj, attr), getattr(testobj_query, attr))
            self.assertNotEquals(testobj.excluded, testobj_query)

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
            session.add(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(CompleteTestClass))
            for attr in ['name', 'boolean', 'enum', 'text', 'longtext',
                         'integer', 'decimal', 'long', 'timestamp',
                         'pythonobject']:
                self.assertEquals(getattr(testobj, attr), getattr(testobj_query, attr))

    def test_many(self):
        pass

    def test_one(self):
        pass
