import tempfile
import unittest

from cryo.backends.sqlite import SQLiteBackend

from .base import BackendTestCase
from ...tests import testclasses


class SQLiteBackendTestCase(unittest.TestCase, BackendTestCase):

    def setUp(self):
        filename = tempfile.mktemp()
        self.backend = SQLiteBackend(filename, modules=[testclasses])
        self.connection = self.backend.newconnection()
        if not self.connection.readtables():
            self.connection.inittables()
            self.connection.createtables(testclasses.gettables())
        