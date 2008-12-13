import tempfile
import unittest

from cryo.backends.sqlite import SQLiteBackend

from .base import BackendTestCaseMixin
from ...tests import testclasses


class SQLiteBackendTestCase(unittest.TestCase, BackendTestCaseMixin):

    def setUp(self):
        filename = tempfile.mktemp()
        self._setUp(SQLiteBackend(filename, modules=[testclasses]))
