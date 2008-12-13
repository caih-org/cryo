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

from . import util


class InvalidValue(Exception):

    def __init__(self, message='', exception=None):
        self.message = message
        self.exception = exception
        Exception.__init__(self)

    def __str__(self):
        return "%s: %s" % (str(self.message), repr(self.exception))


class NotMapped(InvalidValue):

    def __init__(self, class_, exception=None):
        InvalidValue.__init__(self, 'Value class %s is not mapped' %
                              util.fullname(class_), exception)


class TableDoesNotExist(Exception):

    def __init__(self, tablename = '', exception=None):
        self.tablename = tablename
        self.exception = exception
        Exception.__init__(self)

    def __str__(self):
        return "%s: %s" % (str(self.tablename), repr(self.exception))
