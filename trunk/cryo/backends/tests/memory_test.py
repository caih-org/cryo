import unittest
import os
import os.path

from cryo.backends.memory import MemoryBackend

from .base import BackendTestCaseMixin
from ...tests import testclasses


class MemoryBackendTestCase(unittest.TestCase, BackendTestCaseMixin):

    def setUp(self):
        self.backend = MemoryBackend()
        self.connection = self.backend.newconnection()
        if not self.connection.readtables():
            self.connection.inittables()
            self.connection.createtables(testclasses.gettables())
