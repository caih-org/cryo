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

from .. import util
from .. import exceptions
from ..connection import Backend, ConnectedBackend
from ..query import CompareWhereClause, AndWhereClause, OrWhereClause, Field


class MemoryBackend(Backend):

    def __init__(self):
        self.tables = {}
        self.values = {}

    def connect(self, session):
        return MemoryConnectedBackend(self, session)



class MemoryConnectedBackend(ConnectedBackend):

    def __init__(self, backend, session):
        ConnectedBackend.__init__(self, backend, session)
        self._values = {}
        self._deletedvalues = {}

    def createtable(self, table):
        util.QUERY_LOGGER.debug("CREATE TABLE %s" % table.name)
        self.backend.tables[table.name] = True

    def insert(self, *objs):
        for obj in util.flatten(objs):
            hashkey = self.gethashkey(obj) 
            util.QUERY_LOGGER.debug("INSERT %s => %s" % (hashkey, obj))
            self._values[hashkey] = obj

    def delete(self, *objs):
        for obj in util.flatten(objs):
            hashkey = self.gethashkey(obj)
            if hashkey in self._values:
                util.QUERY_LOGGER.debug("DELETE %s => %s" % (hashkey, obj))
                del self._values[hashkey]
            self._deletedvalues[hashkey] = True

    def get(self, table, hashkey):
        util.QUERY_LOGGER.debug("GET %s" % hashkey)
        return self.backend.values[hashkey]

    def query(self, select):
        util.QUERY_LOGGER.debug("SELECT %s" % select)
        table = self.session.connection.tables[select.classname]
        if table.name not in self.backend.tables:
            raise exceptions.TableDoesNotExist(table.name)

        results = []
        count = 0
        start = select.limitclause and select.limitclause.start or 0
        end = select.limitclause and select.limitclause.end
        for key, obj in self.backend.values.items():
            if isinstance(obj, select.class_):
                if self._where(obj, select.whereclause, table):
                    if select.orderbyclauses:
                        results.append(obj)
                    else:
                        if count >= start and (end is None or count < end):
                            hashkey = self.gethashkey(obj)
                            self._values[hashkey] = obj
                            yield obj
                        count += 1

        results.sort(cmp=self._orderby(select.orderbyclauses))

        for obj in results[start:end]:
            hashkey = self.gethashkey(obj)
            self._values[hashkey] = obj
            yield obj

    def _where(self, obj, whereclause, table):
        if whereclause is None:
            return True
        elif isinstance(whereclause, CompareWhereClause):
            return self._compare(obj, whereclause, table)
        elif isinstance(whereclause, AndWhereClause): 
            return (self._where(obj, whereclause.whereclause1, table) and
                    self._where(obj, whereclause.whereclause2, table))
        elif isinstance(whereclause, OrWhereClause): 
            return (self._where(obj, whereclause.whereclause1, table) or
                    self._where(obj, whereclause.whereclause2, table))
        else:
            raise NotImplementedError(whereclause)

    def _compare(self, obj, whereclause, table):
        value1 = whereclause.value1
        value2 = whereclause.value2
        type = int

        if isinstance(value1, Field) and isinstance(value2, Field):
            type = table.columns[value1.name].datatype.type()
            value1 = getattr(obj, value1.name)
            value2 = getattr(obj, value2.name)
        elif isinstance(value1, Field):
            type = table.columns[value1.name].datatype.type()
            value1 = getattr(obj, value1.name)
        elif isinstance(value2, Field):
            type = value1.__class__
            value2 = getattr(obj, value2.name)
        else:
            type = value1.__class__

        if whereclause.comparator == '=':
            return type(value1) == type(value2)
        elif whereclause.comparator == '>':
            return type(value1) > type(value2)
        elif whereclause.comparator == '>=':
            return type(value1) >= type(value2)
        elif whereclause.comparator == '<':
            return type(value1) < type(value2)
        elif whereclause.comparator == '<=':
            return type(value1) <= type(value2)
        elif whereclause.comparator == '!=':
            return type(value1) != type(value2)
        else:
            raise NotImplementedError(whereclause.comparator)

    def _orderby(self, orderbyclauses):
        def cmp_(a, b):
            for orderbyclause in orderbyclauses:
                result = cmp(getattr(a, orderbyclause.field),
                             getattr(b, orderbyclause.field))
                if result:
                    return result
            return cmp(a, b)

        return cmp_

    def commit(self):
        util.QUERY_LOGGER.debug("COMMIT")
        self.backend.values.update(self._values)
        for key, value in self._deletedvalues.items():
            if key in self.backend.values:
                del self.backend.values[key]

    def rollback(self):
        util.QUERY_LOGGER.debug("ROLLBACK")
        self._values = {}
        self._deletedvalues = {}

    def disconnect(self):
        pass
