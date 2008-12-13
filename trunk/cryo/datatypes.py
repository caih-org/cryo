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

from datetime import datetime

import enum

from . import util


class Datatype(object):

    def __init__(self):
        pass

    def __repr__(self):
        return "%s()" % (util.fullname(self.__class__))

    def type(self):
        return lambda x: x


class Unknown(Datatype):

    def __init__(self):
        Datatype.__init__(self)


class LongText(Datatype):

    def __init__(self):
        Datatype.__init__(self)

    def type(self):
        return str

class Text(Datatype):

    def __init__(self, length):
        self.length = length
        Datatype.__init__(self)

    def __repr__(self):
        return "%s(%s)" % (util.fullname(self.__class__), self.length)

    def type(self):
        return str


class Number(Datatype):

    def __init__(self, length, decimals=0):
        self.length = length
        self.decimals = decimals
        Datatype.__init__(self)

    def __repr__(self):
        if self.decimals:
            return "%s(%s, %s)" % (util.fullname(self.__class__), self.length,
                                   self.decimals)
        elif self.length > 1:
            return "%s(%s)" % (util.fullname(self.__class__), self.length)
        else:
            return Datatype.__repr__(self)

    def type(self):
        if decimals:
            return float
        else:
            return int


class Boolean(Number):

    def __init__(self):
        Number.__init__(self, 1)

    def type(self):
        return bool


class Timestamp(Datatype):

    def __init__(self):
        Datatype.__init__(self)


class ForeignKey(Datatype):

    def __init__(self, class_, inverse, autofetch):
        self.class_ = class_
        self.classname = util.fullname(class_)
        self.inverse = inverse
        self.autofetch = autofetch
        Datatype.__init__(self)

    def __repr__(self):
        if self.inverse is None:
            return "%s(%s)" % (util.fullname(self.__class__), self.classname)
        else:
            return "%s(%s, '%s')" % (util.fullname(self.__class__),
                                         self.classname, self.inverse)


class One(ForeignKey):

    def __init__(self, class_, inverse=None, autofetch=True):
        ForeignKey.__init__(self, class_, inverse, autofetch)


class Many(ForeignKey):

    def __init__(self, class_, inverse=None, autofetch=False):
        ForeignKey.__init__(self, class_, inverse, autofetch)


class PythonObject(Datatype):

    def __init__(self):
        Datatype.__init__(self)


class Enum(Datatype):

    def __init__(self, enum):
        Datatype.__init__(self)
        self.enum = enum


def guessdbdatatype(value):
    if value == None:
        return None
    elif isinstance(value, Datatype):
        return value
    elif util.issubclass_(value, Datatype):
        return value()
    elif _issubclassorinstance(value, str):
        return LongText()
    elif _issubclassorinstance(value, bool):
        return Boolean()
    elif _issubclassorinstance(value, float):
        return Number(10, 5)
    elif _issubclassorinstance(value, long):
        return Number(20)
    elif _issubclassorinstance(value, int):
        return Number(10)
    elif _issubclassorinstance(value, datetime):
        return Timestamp()
    elif isinstance(value, enum.Enum):
        return Enum(value)
    elif isinstance(value, enum.EnumValue):
        return Enum(value.enumtype)
    else:
        return Unknown()


def _issubclassorinstance(value, class_):
    return util.issubclass_(value, class_) or isinstance(value, class_)
