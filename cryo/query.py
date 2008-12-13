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

from types import TupleType

from . import util


class Query(object):

    def __init__(self):
        pass


class Select(Query):

    def __init__(self, class_, constructor=None):
        self.constructor = constructor or class_
        self.class_ = class_
        self.classname = util.fullname(class_)
        self.whereclause = None
        self.orderbyclauses = []
        self.limitclause = None
        Query.__init__(self)

    def where(self, value=None, *args):
        if args:
            self.whereclause = CompareWhereClause(value, *args)
        elif isinstance(value, WhereClause):
            self.whereclause = value
        elif value == True:
            self.whereclause = CompareWhereClause(1, '=', 1)
        elif value == False:
            self.whereclause = CompareWhereClause(0, '=', 1)
        else:
            raise ValueError(value)

        return self

    def and_(self, value=None, *args):
        whereclause = args and CompareWhereClause(value, *args) or value
        self.whereclause = AndWhereClause(self.whereclause, whereclause)
        return self

    def or_(self, value=None, *args):
        whereclause = args and CompareWhereClause(value, *args) or value
        self.whereclause = OrWhereClause(self.whereclause, whereclause)
        return self

    def orderby(self, *orderbyclauses):
        for orderbyclause in orderbyclauses:
            if type(orderbyclause) is OrderByClause:
                self.orderbyclauses.append(orderbyclause)
            elif type(orderbyclause) is TupleType:
                self.orderbyclauses.append(OrderByClause(orderbyclause[0],
                                                         orderbyclause[1]))
            else:
                self.orderbyclauses.append(OrderByClause(orderbyclause))
        return self

    def __getslice__(self, start=0, end=None):
        self.limitclause = LimitClause(start, end)
        return self


class Field:

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return CompareWhereClause(self, '=', other)

    def __ne__(self, other):
        return CompareWhereClause(self, '!=', other)

    def __gt__(self, other):
        return CompareWhereClause(self, '>', other)

    def __ge__(self, other):
        return CompareWhereClause(self, '>=', other)

    def __lt__(self, other):
        return CompareWhereClause(self, '<', other)

    def __le__(self, other):
        return CompareWhereClause(self, '<=', other)


class WhereClause(object):

    def __init__(self):
        pass

    def __or__(self, other):
        return OrWhereClause(self, other)
    __ror__ = __or__

    def __and__(self, other):
        return AndWhereClause(self, other)
    __rand__ = __or__


class CompareWhereClause(WhereClause):

    def __init__(self, value1, comparator, value2):
        self.value1 = value1
        self.value2 = value2
        self.comparator = comparator
        WhereClause.__init__(self)


class AndWhereClause(WhereClause):

    def __init__(self, whereclause1, whereclause2):
        self.whereclause1 = whereclause1
        self.whereclause2 = whereclause2
        WhereClause.__init__(self)


class OrWhereClause(WhereClause):

    def __init__(self, whereclause1, whereclause2):
        self.whereclause1 = whereclause1
        self.whereclause2 = whereclause2
        WhereClause.__init__(self)


class OrderByClause(object):

    def __init__(self, field, ascending=True):
        self.field = field
        self.ascending = ascending


class LimitClause(object):

    def __init__(self, start=0, end=None):
        self.start = start
        self.end = end
