from UserDict import DictMixin

from . import exceptions
from . import util


class Session(DictMixin):

    def __init__(self, connection, autocommit=True):
        self.connection = connection
        self.autocommit = autocommit
        self._objs = {}
        self._commited = {}
        self._deleted = {}
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
        if self._deleted:
            self.connectedbackend.delete([value[0] for value in
                                          self._deleted.values()])
        self.connectedbackend.commit()
        self._commited.update(self._objs)

    def rollback(self):
        self.connectedbackend.rollback()
        self._objs = {}
        self._objs.update(self._commited)
        self._deleted = {}

    def same(self, objecta, objectb):
        return (self.gethashkey(objecta) == self.gethashkey(objectb))

    ##########################
    # CONTAINER

    def append(self, obj, dirty=True, recursive=False):
        if dirty:
            self[self.gethashkey(obj)] = None
        self[self.gethashkey(obj)] = obj
        if recursive:
            # TODO: add foreign key objs
            pass

    def remove(self, obj, delete=False):
        hashkey = self.gethashkey(obj)
        if hashkey in self._objs:
            del self._objs[hashkey]
        if delete:
            self._deleted[hashkey] = (obj, hash(obj))

    def __getitem__(self, hashkey):
        return self._objs[hashkey][0]

    def __setitem__(self, hashkey, obj):
        if hashkey in self._objs:
            self._objs[hashkey] = (obj, self._objs[hashkey][1])
        else:
            self._objs[hashkey] = (obj, hash(obj))

    def __delitem__(self, obj):
        self.remove(obj, True)

    def __iter__(self):
        return (obj for (obj, hash_) in self._objs.values())

    def __contains__(self, obj):
        try:
            hashkey = self.gethashkey(obj)
            return hashkey in self._objs and self[hashkey] == obj
        except exceptions.NotMapped:
            return obj in self._objs

    def __len__(self):
        return len(self._objs.values())

    def keys(self):
        return self._objs.keys()

    def clear(self):
        self._objs = {}
        self._commited = {}
        self._deleted = {}

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
            obj = self.query(query).next()
            return obj
        except StopIteration:
            return None 

    def query(self, query):
        objs = self.connectedbackend.query(query)
        for obj in util.flatten(objs):
            self.append(obj, dirty=False, recursive=True)
            yield obj
