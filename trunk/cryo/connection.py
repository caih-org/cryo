from __future__ import with_statement

import hashlib

from . import exceptions
from . import util
from .metadata import Table
from .datatypes import LongText, PythonObject
from .query import Select
from .session import Session

import cryo

_TABLES_TABLE = Table(Table, name = '_cryo_tables',
                      attributes = {'name': LongText(),
                                    'classname': LongText(),
                                    'columns': PythonObject(),
                                    'foreignkeys': PythonObject(),
                                    'primarykey': PythonObject()})
_TABLES_TABLE.primarykey = ('name', )


class Connection(object):

    def __init__(self, backend):
        self.backend = backend
        self.tables = {}

    def readtables(self):
        try:
            self.tables[_TABLES_TABLE.classname] = _TABLES_TABLE
            with Session(self) as session:
                tables = dict([(table.classname, table)
                               for table in session.query(Select(Table))])
                for table in tables.values():
                    table.class_ = eval(table.classname, self.backend.modules)
                self.tables.update(tables)
        except exceptions.TableDoesNotExist:
            return False

        return True

    def inittables(self):
        self.createtables(_TABLES_TABLE)

    def createtables(self, *tables):
        with Session(self) as session:
            for table in util.flatten(tables):
                table = session.connectedbackend.createtable(table)
                self.tables[table.classname] = table


class Backend(object):

    def __init__(self, uri, modules = None):
        self.uri = uri
        self.modules = dict([(module.__name__, module)
                             for module in (modules or [])])
        self.modules[cryo.__name__] = cryo

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
                hash = str(self.gethashkey(value))
                hashkey.update(hash)
            except exceptions.NotMapped:
                if value is None:
                    hashkey.update("_cryo_None")
                else:
                    hashkey.update(str(value))

        return long(str(int(hashkey.hexdigest(), 16))[:18])

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
