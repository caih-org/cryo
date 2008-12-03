import os
import os.path
import unittest

from cryo.backends.sqlite import SQLiteBackend

from .base import BackendTestCase
from ...tests import testclasses


class SQLiteBackendTestCase(unittest.TestCase, BackendTestCase):

    def setUp(self):
        self.tearDown()
        self.backend = SQLiteBackend('./test.sqlite', modules=[testclasses])
        self.connection = self.backend.newconnection()
        if not self.connection.readtables():
            self.connection.inittables()
            self.connection.createtables(testclasses.gettables())

    def tearDown(self):
        if os.path.exists('./test.sqlite'):
            os.unlink('./test.sqlite')
        