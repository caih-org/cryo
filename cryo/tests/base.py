from __future__ import with_statement

from datetime import datetime

from cryo.session import Session
from cryo.backends.sqlite import SQLiteBackend
from cryo.query import Select, Field

from . import testclasses

class BackendTestCase():

    def test_datatypes(self):
        datetime1 = datetime.now()

        with Session(self.connection) as session:
            testobj = testclasses.CompleteTestClass()
            testobj.excluded = 'excluded'
            session.add(testobj)

        with Session(self.connection) as session:
            testobj_query = session.queryone(Select(testclasses.CompleteTestClass))
            for attr in ['name', 'boolean', 'enum', 'text', 'longtext', 'integer'
                         'decimal', 'long', 'timestamp', 'pythonobject']:
                self.assertEquals(getattr(testobj, attr), getattr(testobj_query, attr))
            self.assertNotEquals(testobj.excluded, testobj_query)

        with Session(self.connection) as session:
            testobj = testclasses.CompleteTestClass()
            testobj.name = 'test'
            testobj.boolean = True
            testobj.enum = testclasses.TestEnum.first
            testobj.text = "text"
            testobj.longtext = "x" * 1000
            testobj.integer = 1
            testobj.decimal = 1.0
            testobj.long = 1L
            testobj.timestamp = datetime1
            testobj.pythonobject = True
            session.add(testobj)

        with Session(self.connection) as session:
            testobj = session.queryone(Select(testclasses.CompleteTestClass))
            self.assertEquals(testobj.boolean, False)

    def testMany(self):
        pass

    def testOne(self):
        pass
