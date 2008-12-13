#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2008  César Izurieta

This file is part of Cryo.

Cryo is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__author__ = "César Izurieta"
__email__ = "cesar at caih dot org"
__version__ = "$Revision$"[11:-2]

import unittest

from cryo.backends.memory import MemoryBackend

from .base import BackendTestCaseMixin
from ...tests import testclasses


class MemoryBackendTestCase(unittest.TestCase, BackendTestCaseMixin):

    def setUp(self):
        self._setUp(MemoryBackend())
