from __future__ import with_statement

from datetime import datetime
import random

from cryo.session import Session
from cryo.query import Select, Field

from . import testclasses

class BackendTestCase():

    def test_session(self):
        with Session(self.connection) as session:
            testobj1 = testclasses.CompleteTestClass("1")
            testobj2 = testclasses.CompleteTestClass("2")
    
            self.assertTrue(testobj1 not in session)
            self.assertTrue(testobj2 not in session)
    
            testobj3_1 = testclasses.CompleteTestClass("3")
            testobj3_2 = testclasses.CompleteTestClass("3")
    
            self.assertTrue(session.same(testobj3_1, testobj3_2))
    
            session.add(testobj1)
            session.add(testobj2)
            session.add(testobj3_1)
            session.add(testobj3_2)
    
            self.assertTrue(testobj1 in session)
            self.assertTrue(testobj2 in session)

            del session[testobj3_1]

            self.assertTrue(testobj1 in session)
            self.assertTrue(testobj2 in session)
            self.assertTrue(testobj3_1 not in session)
            self.assertTrue(testobj3_2 not in session)

    def test_rollback(self):
        testobj = testclasses.CompleteTestClass()
        with Session(self.connection) as session:
            session.add(testobj)
            session.rollback()
            self.assertTrue(testobj not in session)

        with Session(self.connection) as session:
            session.add(testobj)
            session.commit()
            del session[testobj]
            session.rollback()
            self.assertTrue(testobj in session)

    def test_datatypes(self):
        testobj = testclasses.CompleteTestClass()
        with Session(self.connection) as session:
            testobj.excluded = 'excluded'
            session.add(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(testclasses.CompleteTestClass))
            for attr in ['name', 'boolean', 'enum', 'text', 'longtext', 'integer',
                         'decimal', 'long', 'timestamp', 'pythonobject']:
                self.assertEquals(getattr(testobj, attr), getattr(testobj_query, attr))
            self.assertNotEquals(testobj.excluded, testobj_query)

        testobj = testclasses.CompleteTestClass()
        with Session(self.connection) as session:
            testobj.name = 'test'
            testobj.boolean = not testobj.boolean
            testobj.enum = testclasses.TestEnum.second
            testobj.text = "text_" + str(random.randint(1, 20))
            testobj.longtext = "x" * 1000
            testobj.integer = 2
            testobj.decimal = 3.0
            testobj.long = 4L
            testobj.timestamp = datetime.now()
            testobj.pythonobject = True
            session.add(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(testclasses.CompleteTestClass))
            for attr in ['name', 'boolean', 'enum', 'text', 'longtext', 'integer',
                         'decimal', 'long', 'timestamp', 'pythonobject']:
                self.assertEquals(getattr(testobj, attr), getattr(testobj_query, attr))

    def test_many(self):
        pass

    def test_one(self):
        pass
