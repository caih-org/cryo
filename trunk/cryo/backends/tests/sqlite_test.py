import unittest
import os
import os.path
import traceback

from cryo.backends.sqlite import SQLiteBackend

from ...tests import base
from ...tests import testclasses

_PATH = './test.sqlite'


class SQLiteBackendTestCase(unittest.TestCase, base.BackendTestCase):

    def setUp(self):
        try:
            self.backend = SQLiteBackend(_PATH, modules=[testclasses])
            self.connection = self.backend.newconnection()
            if not self.connection.readtables():
                self.connection.createtables(testclasses.gettables())
        except Exception, e:
            self.tearDown()
            self.fail(traceback.format_exc())

    def tearDown(self):
        if os.path.exists(_PATH):
            os.unlink(_PATH)
