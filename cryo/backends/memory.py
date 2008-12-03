from .. import util
from .. import exceptions
from .. import datatypes
from ..connection import Backend, ConnectedBackend

class MemoryBackend(Backend):

    def __init__(self):
        self.values = {}

    def connect(self, session):
        return MemoryConnectedBackend(self, session)



class MemoryConnectedBackend(ConnectedBackend):

    def __init__(self, backend, session):
        ConnectedBackend.__init__(self, backend, session)
        self.values = {}

    def createtable(self, table):
        self.backend.values[table.name] = {}
        return table

    def insert(self, *objs):
        for obj in util.flatten(objs):
            table = self.session.gettable(obj)
            hashkey = self.gethashkey(obj) 
            self.backend.values[table.name][hashkey] = obj

    def delete(self, *objs):
        for obj in util.flatten(objs):
            table = self.session.gettable(obj)
            hashkey = self.gethashkey(obj) 
            del self.backend.values[table.name][hashkey]

    def get(self, table, hashkey):
        return self.backend.values[table.name][hashkey]

    def query(self, query):
        results = []
        for value in self.backend.values:
            if util.issubclass_(value, query.class_):
                results.append(value)

        # TODO where(continue), sort, limit
        
        return results

    def commit(self):
        self.backend.values.update(self.values)
        self.values = {}

    def rollback(self):
        self.values = {}

    def disconnect(self):
        pass
