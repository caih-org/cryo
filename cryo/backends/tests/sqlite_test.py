import unittest
import os

from ..sqlite import SQLiteBackend

from ...tests import base

from ...tests import testclasses

_path = './test.sqlite';


class SQLiteBackendTestCase(unittest.TestCase, base.BackendTestCase):

    def setUp(self):
        self.backend = SQLiteBackend(_path, modules=[testclasses])
        self.connection = self.backend.newconnection()
        if not self.connection.readtables():
            self.connection.createtables(testclasses.gettables())

    def tearDown(self):
        os.unlink(_path)
