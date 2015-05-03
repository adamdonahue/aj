# graph API model

import copy
import sqlalchemy.event
import sqlalchemy.ext.declarative
import sqlalchemy.inspection
import sqlalchemy.orm
import types

from .graph import *
from .editable import *
from pprint import pprint

import broom

# The ENABLE_ constant(s) below are to enable/disable certain
# experimental features, or features that need further
# testing and/or performance tuning.
# TODO: Move these to a configuration file.
ENABLE_DELEGATE_ON_INIT = False

ReadOnly     = NodeDescriptor.READONLY
Overlayable  = NodeDescriptor.OVERLAYABLE
Settable     = NodeDescriptor.SETTABLE
Serializable = NodeDescriptor.SERIALIZABLE
Stored       = NodeDescriptor.STORED

class BroomTypeBase(object):
    def __init__(cls, name, bases, attrs):
        if '__init__' in attrs:
            raise RuntimeError("Subclasses of BroomObject are not permitted "
                               "to redefine __init__.")

        for k,v in attrs.iteritems():
            if not isinstance(v, FieldDescriptor):
                continue
            if v.name is None:
                v._name = k
            elif v.name != k:
                v_ = copy.copy(v)
                v_._name = k
                v_._flags = v.flags
                setattr(cls, k, v_)

        descriptors = []
        for k in dir(cls):
            v = getattr(cls, k)
            if isinstance(v, FieldDescriptor):
                descriptors.append(v)
        cls._fieldDescriptors = descriptors
        cls._fieldNames = [f.name for f in descriptors]
        cls._storedFieldNames = [f.name for f in descriptors if f.stored]

class BroomType(BroomTypeBase, sqlalchemy.ext.declarative.api.DeclarativeMeta):
    def __init__(cls, name, bases, attrs):
        BroomTypeBase.__init__(cls, name, bases, attrs)

        # FIXME: This is a hack until I figure out how to better
        #        handle table aliased on subclasses.
        if '__tablename__' in attrs or '__mapper_args__' in attrs:
            sqlalchemy.ext.declarative.api.DeclarativeMeta.__init__(
                    cls, name, bases, attrs
                    )

class FieldDescriptor(NodeDescriptor):
    pass

class Field(NodeDescriptorBound):
    pass

class StoredField(Field):
    def __init__(self, *args, **kwargs):
        super(StoredField, self).__init__(*args, **kwargs)
        self._ref = getattr(self._obj.__class__, self.descriptor.ref)
        sqlalchemy.event.listen(self._ref, 'set', self.onSet)
        sqlalchemy.event.listen(self._ref, 'append', self.onAppend)
        sqlalchemy.event.listen(self._ref, 'remove', self.onRemove)

    # TODO: Have onSet, onAppend, and onRemove merely
    #       invalidate the underlying nodeData in the root
    #       data store.
    #
    # TODO: Also, do we enforce uniqueness here?
    def onSet(self, target, value, oldvalue, initiator):
        super(StoredField, self).setValue(value)

    def onAppend(self, target, value, initiator):
        collection = list(self())
        collection.append(value)
        super(StoredField, self).setValue(collection)

    def onRemove(self, target, value, initiator):
        collection = list(self())
        if value in collection:
            collection.remove(value)
        super(StoredField, self).setValue(collection)

    def setValue(self, value):
        setattr(self.obj, self.descriptor.ref, value)

    def clearValue(self):
        setattr(self.obj, self.descriptor.ref, None)

class BroomObjectMetadata(object):

    def __init__(self, obj):
        self._m = sqlalchemy.inspection.inspect(obj.__class__)
        self._s = sqlalchemy.inspection.inspect(obj)

    @property
    def attrs(self):
        return tuple(self._m.attrs)

    @property
    def attrs_by_name(self):
        return dict(self._m.attrs)

    @property
    def columns(self):
        return tuple(self._m.columns)

    @property
    def column_names(self):
        return self.columns_by_name.keys()

    @property
    def columns_by_name(self):
        return dict(self._m.columns)

    @property
    def relationships(self):
        return tuple(self._m.relationships)

    @property
    def relationship_names(self):
        return self.relationships_by_name.keys()

    @property
    def relationships_by_name(self):
        return dict(self._m.relationships)

    @property
    def primary_key_columns(self):
        return tuple(self._m.primary_key)

    @property
    def primary_key_columns_by_name(self):
        return dict(self._m.primary_key)

    @property
    def primary_key_column_names(self):
        return tuple([v.name for v in self.primary_key_columns])

    @property
    def primary_key(self):
        return tuple(self._m.primary_key_from_instance(self._s.object))

    @property
    def primary_key_list(self):
        return zip(self.primary_key_column_names, self.primary_key)

    @property
    def primary_key_map(self):
        return dict(self.primary_key_list)

    @property
    def isnew(self):
        return not self._s.persistent

    @property
    def isdeleted(self):
        return self._s.deleted

class BroomObjectBase(object):

    @classmethod
    def _field(cls, obj, v):
        return (StoredField if v.stored else Field)(obj, v)

    def __new__(cls, *args, **kwargs):
        obj = super(BroomObjectBase, cls).__new__(cls, *args, **kwargs)
        for v in obj._fieldDescriptors:
            super(BroomObjectBase, obj).__setattr__(v.name, cls._field(obj, v))
        return obj

    @sqlalchemy.orm.reconstructor
    def initialize(self):
        self._db = self._sa_instance_state.session._db

    def __init__(self, *args, **kwargs):
        for k in kwargs.copy():
            if k not in self._fieldNames:
                continue
            value = kwargs.pop(k)
            field = getattr(self, k)
            if not ENABLE_DELEGATE_ON_INIT:
                if field.delegate:
                    raise RuntimeError("Changes to %s are delegated and "
                                       "cannot be set during object "
                                       "initialization." % field.name
                                       )
            field._setData(value)
            # self.__setattr__(field.name, value)

        # TODO: In theory we don't want a user to set arbitrary
        #       values, at least I don't think we do.  But we
        #       need this for now for two reasons:
        #         (i)  To set database fields not yet modeled as
        #              stored fields.
        #         (ii) As a workaround allowing us to define read-
        #              only graph fields that when read still need
        #              a value (e.g., keys) but whose value once
        #              generated should not change.
        # TODO: This -should- now only set non-Fields, which would
        #       include, at the moment, the database _storedFields.
        #       Once merged we can remove the special stored
        #       fields handling.
        for k,v in kwargs.items():
            setattr(self, k, v)

        # TODO: Revisit.  We always set db on BroomObjects, even
        #       if the object itself is not storable.  This way
        #       a BroomObject knows its context.
        if not hasattr(self, '_db'):
            self._db = broom.db
        # TODO: Long-term we don't want to add the object here because
        #       it breaks merges, and also it's more of a write-time
        #       oriented call.
        #
        #       For now it's here, and we do an expunge whenever a
        #       merge is issued.
        if hasattr(self.__class__, '__tablename__'):
            self._db._session.add(self)

    def __setattr__(self, n, v):
        if n in self._fieldNames:
            c = getattr(self, n)
            c.setValue(v)
            return
        super(BroomObjectBase, self).__setattr__(n, v)

    def toDict(self,
               extra=False,
               meta=False,
               relationships=False,
               expand=False
               ):
        data = dict((k,getattr(self,k)()) for k in self._storedFieldNames)

        # FIXME: Generalize these recursions on lists/tuples and BroomObjects.
        if extra:
            for k in self.ExtraToDictFields():
                v = getattr(self, k)()
                if isinstance(v, broom.BroomObject):
                    v = v.toDict()
                elif isinstance(v, (list,tuple)):
                    v = [o.toDict() if isinstance(o, broom.BroomObject) else o for o in v]
                data[k] = v
        if meta:
            data['broom:meta'] = {'object_type': self.__class__.__name__,
                                  'object_id_fields': self.meta.primary_key_column_names,
                                  'object_id': self.pk,
                                  'object_id_map': self.meta.primary_key_map
                                  }
        if relationships or expand:
            for n in self.meta.relationships_by_name:
                rs = getattr(self, n)
                # TODO: Determine cardinality of relationship using
                #       the native libraries, not this test.
                if expand:
                    if isinstance(rs, (list,tuple)):
                        data[n] = [r.toDict(meta=meta) for r in rs]
                    else:
                        data[n] = rs.toDict(meta=meta) if rs else None
                else:
                    if isinstance(rs, (list,tuple)):
                        data[n] = [(r.__class__.__name__, r.pk) for r in rs]
                    else:
                        data[n] = (rs.__class__.__name__, rs.pk)
        return data

    def printDict(self, *args, **kwargs):
        pprint(self.toDict(*args, **kwargs))

    @property
    def db(self):
        return getattr(self, '_db', None)

    @property
    def meta(self):
        return getattr(self, '_meta', BroomObjectMetadata(self))

    def isnew(self):
        return self.meta.isnew

    def write(self):
        raise NotImplementedError("Writes are allowed only at the session level.")

    def delete(self):
        self.db.delete(self)

    def isdeleted(self):
        return self.meta.isdeleted

    def ismodified(self):
        return self.db.modified(self)

    def isdirty(self):
        return self.db.dirty(self)

    @property
    def id(self):
        return self.pk

    @property
    def pk(self):
        if not self.meta:
            return
        return self.meta.primary_key

    def query(self):
        return self.db.query(self.__class__)

    @classmethod
    def create_schema(cls, db):
        cls.metadata.create_all(db.engine)

    def __repr__(self):
        if not self.stored():
            return object.__repr__(self)
        return '<%s %s>' % (
                self.__class__.__name__,
                "{" + ", ".join("%s: %s" % (k,v) for k,v in self.meta.primary_key_list) + "}"
                )

    def to_json(self):
        return broom.BroomObjectSerializer.serialize(self)

    @classmethod
    def from_json(self, data):
        return broom.BroomObjectSerializer.deserialize(data)

    def ExtraToDictFields(self):
        return []

    @classmethod
    def stored(cls):
        return hasattr(cls, '__tablename__')


BroomObject = sqlalchemy.ext.declarative.declarative_base(cls=BroomObjectBase,
                                                          name='BroomObject',
                                                          constructor=None,
                                                          metaclass=BroomType
                                                          )

BroomObjectType = sqlalchemy.ext.declarative.api.DeclarativeMeta

def field(f=0, flags=ReadOnly, *args, **kwargs):
    """Declare an on-graph field."""
    if not isinstance(f, types.FunctionType):
        def wrapper(g):
            return field(g, f, *args, **kwargs)
        return wrapper
    # TODO: Remove this test when the stored() function is merged
    #       with this one.
    if flags & Stored == Stored:
        raise NotImplementedError("You cannot yet define a stored field "
                                  "via the field decorator.  Use the "
                                  "stored function instead.")
    return FieldDescriptor(f, flags, f.__name__, *args, **kwargs)


# TODO: Merge with 'field' above.
def stored(ref):
    if not isinstance(ref, str):
        raise RuntimeError("You must refer to underlying column names "
                           "using a string value.")
    def f(self):
        return getattr(self, ref)
    return FieldDescriptor(f, flags=Stored, ref=ref)

# We alias other sqlalchemy classes here, for future expansion.
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.dialects.postgresql import INET

# Here we add some custom classes (which may exist already
# as extensions, but are here until we know for sure).
#
# These are shortcuts to the full sqlalchemy definitions
# we'd use.

def Serial(table_name, *args, **kwargs):
    return Column(Integer, *args, **kwargs)

