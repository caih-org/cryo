import unittest

from cryo.backends.sqlite import SQLiteBackend

from ...tests import base
from ...tests import testclasses


class SQLiteBackendTestCase(unittest.TestCase, base.BackendTestCase):

    def setUp(self):
        self.backend = SQLiteBackend(":memory:", modules=[testclasses])
        self.connection = self.backend.newconnection()
        if not self.connection.readtables():
            self.connection.createtables(testclasses.gettables())

