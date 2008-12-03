from .. import util
from .. import exceptions
from .. import datatypes
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
        self.values = {}
        self.deletedvalues = {}

    def createtable(self, table):
        self.backend.tables[table.name] = True
        return table

    def insert(self, *objs):
        for obj in util.flatten(objs):
            table = self.session.gettable(obj)
            hashkey = self.gethashkey(obj) 
            self.values[hashkey] = obj

    def delete(self, *objs):
        for obj in util.flatten(objs):
            table = self.session.gettable(obj)
            hashkey = self.gethashkey(obj) 
            del self.values[hashkey]
            self.deletedvalues[hashkey] = True

    def get(self, table, hashkey):
        return self.backend.values[hashkey]

    def query(self, select):
        table = self.session.connection.tables[select.classname]

        if table.name not in self.backend.tables:
            raise exceptions.TableDoesNotExist(table.name)
        results = []
        for value in self.backend.values:
            if util.issubclass_(value, select.class_):
                results.append(value)

        # TODO where(continue), sort, limit
        
        for result in results:
            yield results

    def commit(self):
        self.backend.values.update(self.values)
        self.values = []
        # TODO delete values from backend

    def rollback(self):
        self.values = {}

    def disconnect(self):
        pass
