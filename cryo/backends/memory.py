from .. import util
from .. import exceptions
from ..connection import Backend, ConnectedBackend


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
            table = self.session.gettable(obj)
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
        for key, value in self.backend.values.items():
            if isinstance(value, select.class_):
                # TODO where(just use continue)
                if True:
                    if select.orderbyclauses:
                        results.append(value)
                    elif count >= start and (end is None or count < end):
                        yield value
                        count += 1

        for result in results[start : end]:
            yield result

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
