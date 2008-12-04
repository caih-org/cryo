import sqlite3
import pickle
import base64

from .standardsql import StandardSQLBackend, StandardSQLConnectedBackend
from .. import util
from .. import exceptions
from .. import datatypes


def _todb(value):
    """Converts a value to be stored on the database"""

    if hasattr(value, '__iter__'):
        return [_todb(val) for val in value]
    elif not isinstance(value, StandardSQLConnectedBackend.Wrapper):
        return value
    elif isinstance(value.column.datatype, datatypes.Enum):
        return value.value.index
    elif isinstance(value.column.datatype, datatypes.PythonObject):
        return base64.encodestring(pickle.dumps(value.value, 2))
    if isinstance(value.column.datatype, datatypes.ForeignKey):
        return value.connectedbackend.gethashkey(value.value)
    else:
        return value.value


def _fromdb(value, column):
    """Converts a value pulled from the database"""

    class_ = column.datatype.__class__

    if issubclass(class_, datatypes.PythonObject):
        return pickle.loads(base64.decodestring(value))
    elif issubclass(class_, datatypes.Boolean):
        return value == True or int(value) == 1
    elif issubclass(class_, datatypes.Enum):
        return column.datatype.enum[int(value)]
    elif issubclass(class_, datatypes.One):
        # TODO: handle foreign keys
        return value
    elif issubclass(class_, datatypes.Many):
        # TODO: handle foreign keys
        return []
    else:
        return value


class SQLiteBackend(StandardSQLBackend):

    def __init__(self, uri, modules=None):
        StandardSQLBackend.__init__(self, uri, modules)

    def connect(self, session):
        return SQLiteConnectedBackend(self, session)


class SQLiteConnectedBackend(StandardSQLConnectedBackend):

    def __init__(self, backend, session):
        StandardSQLConnectedBackend.__init__(self, backend, session)
        self.connection = sqlite3.connect(backend.uri,
                                          detect_types=sqlite3.PARSE_COLNAMES)
        self.connection.row_factory = sqlite3.Row

    def createtable(self, table):
        query = self._createtable(table)
        util.QUERY_LOGGER.debug(query)
        self.connection.execute(query)
        self.insert(table)
        return table

    def gettype(self, datatype):
        if isinstance(datatype, datatypes.PythonObject):
            return 'text'
        elif isinstance(datatype, datatypes.Number):
            return 'number(%s, %s)' % (datatype.length, datatype.decimals)
        elif isinstance(datatype, datatypes.Timestamp):
            return 'timestamp'
        elif isinstance(datatype, datatypes.ForeignKey):
            return 'integer'
        else:
            return 'text'

    def insert(self, *objs):
        for query, values in self._insert(*objs):
            util.QUERY_LOGGER.debug("%s => %s" % (query, _todb(values)))
            self.connection.execute(query, _todb(values))

    def delete(self, *objs):
        for query, values in self._delete(*objs):
            util.QUERY_LOGGER.debug("%s => %s" % (query, _todb(values)))
            self.connection.execute(query, _todb(values))

    def query(self, select):
        table = self.session.connection.tables[select.classname]

        columns = ["'%s'.'%s' AS '%s [%s]'" %
                   (table.name, column.name, column.name,
                    util.fullname_underscore(column.datatype.__class__))
                   for (name, column) in table.columns.items()]

        query, values = self._query(select, columns=columns)

        try:
            util.QUERY_LOGGER.debug("%s => %s" % (query, _todb(values)))
            results = self.connection.execute(query, _todb(values))

            for row in results:
                yield self._createobj(row, table, select.constructor)

        except sqlite3.OperationalError, e:
            raise exceptions.TableDoesNotExist(table.name, e)

    def _createobj(self, row, table, constructor):
        obj = constructor()
        for name, column in table.columns.items():
            if isinstance(column.datatype, datatypes.One):
                # TODO: check for autofetch
                class_ = column.datatype.class_
                value = self.session.get(class_, row[column.name])
                setattr(obj, name, value)
            elif isinstance(column.datatype, datatypes.Many):
                # TODO: get collection or set proxy
                value = []
                setattr(obj, name, value)
            else:
                value = _fromdb(row[column.name], column)
                setattr(obj, name, value)

        return obj

    def commit(self):
        util.QUERY_LOGGER.debug("COMMIT")
        self.connection.commit()

    def rollback(self):
        util.QUERY_LOGGER.debug("ROLLBACK")
        self.connection.rollback()

    def disconnect(self):
        self.connection.close()
        self.connection = None
