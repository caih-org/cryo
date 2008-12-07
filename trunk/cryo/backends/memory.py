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
        return table

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
                if self._where(obj, select.whereclause):
                    if select.orderbyclauses:
                        results.append(obj)
                    elif count >= start and (end is None or count < end):
                        hashkey = self.gethashkey(obj)
                        self._values[hashkey] = obj
                        yield obj
                        count += 1

        for obj in results[start:end]:
            hashkey = self.gethashkey(obj)
            self._values[hashkey] = obj
            yield obj

    def _where(self, obj, whereclause):
        if whereclause is None:
            return True
        elif isinstance(whereclause, CompareWhereClause):
            return self._compare(obj, whereclause)
        elif isinstance(whereclause, AndWhereClause): 
            return (self._where(obj, whereclause.whereclause1) and
                    self._where(obj, whereclause.whereclause2))
        elif isinstance(whereclause, OrWhereClause): 
            return (self._where(obj, whereclause.whereclause1) or
                    self._where(obj, whereclause.whereclause2))
        else:
            raise NotImplementedError(whereclause)

    def _compare(self, obj, whereclause):
        value1 = whereclause.value1
        value2 = whereclause.value2

        if isinstance(value1, Field):
            value1 = getattr(obj, value1.name)

        if isinstance(value2, Field):
            value2 = getattr(obj, value2.name)

        if whereclause.comparator == '='
            return value1 == value2
        elif whereclause.comparator == '>'
            return value1 > value2
        elif whereclause.comparator == '>='
            return value1 >= value2
        elif whereclause.comparator == '<'
            return value1 < value2
        elif whereclause.comparator == '<='
            return value1 <= value2
        elif whereclause.comparator == '!='
            return value1 <= value2
        else:
            raise NotImplementedError(whereclause.comparator)

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
