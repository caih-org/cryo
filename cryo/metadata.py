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

from .datatypes import guessdbdatatype, ForeignKey, Many, Unknown
from . import util


class Table(object):

    def __init__(self, class_=None, name=None, attributes=None, example=None,
                 primarykey=None):
        if class_ is not None:
            attributes = attributes or {}
            obj = example or class_()
            for attr in obj.__dict__:
                if attr[0] != '_' and not attr in attributes:
                    value = getattr(obj, attr)
                    if value == None:
                        attributes[attr] = None
                    else:
                        attributes[attr] = value

            self.name = name or class_.__name__
            self.class_ = class_
            self.classname = util.fullname(class_)
            self.columns = {}
            self.foreignkeys = {}
            self._generatecolumns(attributes)
            self.primarykey = primarykey or tuple(sorted(self.columns.keys()))
            if isinstance(self.primarykey, str):
                self.primarykey = (self.primarykey, )

    def _generatecolumns(self, attributes):
        for attr, value in attributes.items():
            if isinstance(value, Column):
                self._addcolumn(attr, value)
            else:
                dbdatatype = guessdbdatatype(value)
                if dbdatatype:
                    self._addcolumn(attr, Column(attr, dbdatatype))

    def _addcolumn(self, attr, column):
        if isinstance(column.datatype, ForeignKey):
            self.foreignkeys[attr] = column

        if (not isinstance(column.datatype, Many) and
            not isinstance(column.datatype, Unknown)):
            self.columns[attr] = column


class Column(object):

    def __init__(self, name, datatype):
        self.name = name
        self.datatype = datatype

    def __repr__(self):
        return "%s('%s', %s)" % (util.fullname(self.__class__), self.name,
                                 self.datatype)
