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

from __future__ import with_statement

__author__ = "César Izurieta"
__email__ = "cesar at caih dot org"
__version__ = "$Revision$"[11:-2]

import hashlib

from . import exceptions
from . import util
from .metadata import Table
from .datatypes import LongText, PythonObject
from .session import Session

import cryo


class Connection(object):

    def __init__(self, backend):
        self.backend = backend
        self.tables = {}

    def setup(self, *tables):
        # FIXME: check if we need to update!
        with Session(self) as session:
            for table in util.flatten(tables):
                session.connectedbackend.createtable(table)
                self.tables[table.classname] = table


class Backend(object):

    def __init__(self, uri, modules = None):
        self.uri = uri
        self.modules = dict([(util.fixtest(module.__name__), module)
                             for module in (modules or [])])
        self.modules[util.fixtest(cryo.__name__)] = cryo

    def newconnection(self):
        return Connection(self)

    def connect(self):
        pass


class ConnectedBackend(object):

    def __init__(self, backend, session):
        self.backend = backend
        self.session = session

    def gethashkey(self, obj):
        table = self.session.gettable(obj)
        return self._gethashkey(obj, table, table.primarykey)

    def getfullhashkey(self, obj):
        table = self.session.gettable(obj)
        return self._gethashkey(obj, table, table.columns.keys())

    def _gethashkey(self, obj, table, attributes):
        fullname = util.fullname(obj.__class__)
        if fullname != table.classname:
            raise exceptions.InvalidValue('Value is not of table\'s ' +
                                          'class: %s != %s'
                                          % (fullname, table.classname))
        hashkey = hashlib.sha1()
        hashkey.update(fullname)
        for attr in attributes:
            value = getattr(obj, attr)
            try:
                valuehash = str(self.gethashkey(value))
                hashkey.update(valuehash)
            except exceptions.NotMapped:
                if value is None:
                    hashkey.update("_cryo_None")
                else:
                    hashkey.update(str(value))

        return hashkey.hexdigest()

    def createtable(self, table):
        raise NotImplementedError()

    def insert(self, *objs):
        raise NotImplementedError()

    def delete(self, *objs):
        raise NotImplementedError()

    def get(self, table, hashkey):
        raise NotImplementedError()

    def query(self, query):
        raise NotImplementedError()

    def commit(self):
        raise NotImplementedError()

    def rollback(self):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()
