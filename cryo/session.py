from . import exceptions
from . import util


class Session(object):

    def __init__(self, connection, autocommit=True):
        self.connection = connection
        self.autocommit = autocommit
        self._objs = {}
        self._deletedobjs = {}
        self.connectedbackend = self.connection.backend.connect(self)

    def gettable(self, obj=None, classname=None, class_=None):
        classname = classname or util.fullname(class_ or obj.__class__)
        if classname not in self.connection.tables:
            raise exceptions.NotMapped(obj.__class__)
        return self.connection.tables[classname]

    def gethashkey(self, obj):
        return self.connectedbackend.gethashkey(obj)

    def commit(self):
        for value, hash_ in self._objs.values():
            if hash(value) != hash_:
                self.connectedbackend.insert(value)
        if self._deletedobjs:
            self.connectedbackend.delete([value[0] for value in
                                          self._deletedobjs.values()])
        self.connectedbackend.commit()

    def rollback(self):
        self.connectedbackend.rollback()
        self._objs.update(self._deletedobjs)
        self._deletedobjs = {}

    def same(self, objecta, objectb):
        return (self.gethashkey(objecta) == self.gethashkey(objectb))

    ##########################
    # CONTAINER

    def add(self, obj, dirty=True):
        if dirty:
            self[self.gethashkey(obj)] = None
        self[self.gethashkey(obj)] = obj

    def __getitem__(self, hashkey):
        return self._objs[hashkey][0]

    def __setitem__(self, hashkey, obj):
        if hashkey in self._objs:
            self._objs[hashkey] = (obj, self._objs[hashkey][1])
        else:
            self._objs[hashkey] = (obj, hash(obj))

    def __delitem__(self, obj):
        hashkey = self.gethashkey(obj)
        if hashkey in self._objs:
            del self._objs[hashkey]
        self._deletedobjs[hashkey] = (obj, hash(obj))

    def __iter__(self):
        return (obj for (obj, hash_) in self._objs.values())

    def __contains__(self, obj):
        try:
            return (obj in self._objs or
                    self.gethashkey(obj) in self._objs)
        except exceptions.NotMapped:
            return False

    ##########################
    # WITH

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            self.rollback()
        elif self.autocommit:
            self.commit()

        self.connectedbackend.disconnect()

    ##########################
    # QUERY

    def get(self, class_, hashkey):
        if hashkey in self:
            return self[hashkey]
        else:
            table = self.gettable(class_=class_)
            return self.connectedbackend.get(table, hashkey)

    def queryone(self, query):
        try:
            return self.query(query).next()
        except StopIteration:
            return None 

    def query(self, query):
        objs = self.connectedbackend.query(query)
        for obj in util.flatten(objs):
            self.add(obj, dirty = False)
            yield obj