import unittest
import os
import os.path

from cryo.backends.memory import MemoryBackend

from ...tests import base


class MemoryBackendTestCase(unittest.TestCase, base.BackendTestCase):

    def setUp(self):
        self.backend = MemoryBackend()
        self.connection = self.backend.newconnection()
        if not self.connection.readtables():
            self.connection.createtables(testclasses.gettables())
