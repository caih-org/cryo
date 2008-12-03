import unittest
import os
import os.path

from cryo.backends.memory import MemoryBackend

from .base import BackendTestCase
from ...tests import testclasses


class MemoryBackendTestCase(unittest.TestCase, BackendTestCase):

    def setUp(self):
        self.backend = MemoryBackend()
        self.connection = self.backend.newconnection()
        if not self.connection.readtables():
            self.connection.createtables(testclasses.gettables())
