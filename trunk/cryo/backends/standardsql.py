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
from ..query import Select, CompareWhereClause, AndWhereClause, \
                    OrWhereClause, Field

_ID_FIELD_NAME = '_cryo_id'


class StandardSQLBackend(Backend):

    def __init__(self, uri, modules = None):
        Backend.__init__(self, uri, modules)


class StandardSQLConnectedBackend(ConnectedBackend):

    def __init__(self, backend, session):
        ConnectedBackend.__init__(self, backend, session)

    def _createtable(self, table):
        columndefinitions = ["'%s' %s" %
                             (column.name, self.gettype(column.datatype))
                             for column in table.columns.values()]
        return "CREATE TABLE '%s' (%s PRIMARY_KEY UNIQUE, %s)" % \
                            (table.name, _ID_FIELD_NAME,
                             ", ".join(columndefinitions))

    def gettype(self, datatype):
        raise NotImplementedError()

    def _insert(self, *objs):
        for obj in util.flatten(objs):
            table = self.session.gettable(obj)

            names = [_ID_FIELD_NAME]
            values = [self.gethashkey(obj)]

            for name, column in table.columns.items():
                names.append("'%s'" % column.name)
                wrapped = self.Wrapper(self, column, getattr(obj, name))
                values.append(wrapped)

            options = ', '.join(['?' for name in names])

            query = ("INSERT OR REPLACE INTO '%s' (%s) VALUES (%s)"
                     % (table.name, ", ".join(names), options))

            yield query, values

    def _delete(self, *objs):
        for obj in util.flatten(objs):
            table = self.session.gettable(obj)
            query = "DELETE FROM '%s' WHERE %s = ?" % (table.name,
                                                       _ID_FIELD_NAME)
            yield query, [self.gethashkey(obj)]

    def get(self, table, hashkey):
        results = self.query(Select(table.class_).where(Field(_ID_FIELD_NAME),
                                                        "=", hashkey))
        for result in results:
            return result

    def _query(self, query, columns=''):
        table = self.session.connection.tables[query.classname]

        columns = columns or ["'%s'.'%s'" % (table.name, column.name)
                              for (name, column) in table.columns.items()]

        queryparts = []
        queryparts.append("SELECT %s" % ", ".join(columns))
        queryparts.append("FROM '%s'" % table.name)

        values = []
        if query.whereclause:
            where, values = self._where(table.name, query.whereclause)
            queryparts.append("WHERE %s" % where)

        if query.orderbyclauses:
            queryparts.append("ORDER BY")
            orderby = []
            for orderbyclause in query.orderbyclauses:
                orderby.append("'%s'.'%s' %s" % (table.name,
                                                 orderbyclause.field,
                                                 orderbyclause.ascending
                                                 and "ASC" or "DESC"))
            queryparts.append(", ".join(orderby))

        if query.limitclause:
            queryparts .append("LIMIT %s" % query.limitclause.start)
            if query.limitclause.end:
                queryparts.append(", %s" % (query.limitclause.end -
                                            query.limitclause.start))

        return " ".join(queryparts), values

    def _where(self, tablename, whereclause):
        if type(whereclause) is CompareWhereClause:
            query1, query2, values = self._value(tablename, whereclause.value1,
                                                 whereclause.value2)
            return "%s %s %s" % (query1, whereclause.comparator,
                                 query2), values

        elif type(whereclause) is AndWhereClause:
            whereclause1 = self._where(tablename, whereclause.whereclause1)
            whereclause2 = self._where(tablename, whereclause.whereclause2)

            return "(%s AND %s)" % (whereclause1[0], whereclause2[0]), \
                   whereclause1[1] + whereclause2[1]

        elif type(whereclause) is OrWhereClause:
            whereclause1 = self._where(tablename, whereclause.whereclause1)
            whereclause2 = self._where(tablename, whereclause.whereclause2)

            return "(%s OR %s)" % (whereclause1[0], whereclause2[0]), \
                   whereclause1[1] + whereclause2[1]

    def _value(self, tablename, value1, value2):
        values = []

        # TODO: wrap values using _todb?
        if not isinstance(value1, Field) and not isinstance(value2, Field):
            values = [value1, value2]
        elif not isinstance(value1, Field):
            values = [value1]
        elif not isinstance(value2, Field):
            values = [value2]

        return (self._field(tablename, value1),
                self._field(tablename, value2),
                values)

    def _field(self, tablename, field, useid=False):
        if not isinstance(field, Field):
            return "?"
        elif useid:
            return "'%s'.'%s'.%s" % (tablename, field.name, _ID_FIELD_NAME)
        else:
            return "'%s'.'%s'" % (tablename, field.name)

    class Wrapper(object):

        def __init__(self, connectedbackend, column, value):
            self.connectedbackend = connectedbackend
            self.column = column
            self.value = value
