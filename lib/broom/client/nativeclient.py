"""BroomDB client.

Client for management of persisted BroomObject instances.

"""
import broom

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable
from .exception import BroomDBObjectNotFoundError, BroomDBClientError

def instance_load_handler(target, context):
    if target.db and target.db != target._sa_instance_state.session._db:
        raise RuntimeError("Inconsistent database state.")
    if target.db:
        return
    target._db = target._sa_instance_state.session._db

def localdb():
    return BroomDBClient.connect("sqlite:///:memory:")

class BroomDBClient(object):
    """Database access actually happens via a BroomDBSession.

    A BroomDBClient is essentially a wrapper around a global session
    that exposes that session's methods directly for convenience.

    That is, a user can do either of the following:

        o = broom.db.read( ... )

        session = broom.db.session()
        o = session.db.read( ... )

    """
    @classmethod
    def connect(cls, uri, *args, **kwargs):
        engine = create_engine(uri, *args, **kwargs)
        return cls(engine)

    def __init__(self, engine):
        self._engine = engine
        # TODO: Add a clean transaction-handling implementation.
        # TODO: Figure out whether we can set autoflush=True
        #       without breaking the model.
        # TODO: Do the bind later, as part of configure.
        self._Session = sessionmaker(bind=self._engine,
                                     autoflush=False,
                                     autocommit=False,
                                     expire_on_commit=False
                                     )

        # TODO: Enable threads on the client.  To do so we'll need
        #       to use session more akin to a transaction.
        #       
        self._session = self._Session()
        self._transactionContext = None

        # Backpopulate _db on the session so we can get it
        # during instance loads.
        self._session._db = self

    @property
    def engine(self):
        return self._engine

    def session(self):
        raise NotImplementedError("Sessions are not yet implemented.")

    # TODO: Merge session with Session, and get rid of the 'global'
    #       session in favor of a default session for cases where
    #       the user connects to a database via the shell for example.
    #       Ultimately we want the user to not have to create a session
    #       specifically, but to have the ability to do so when needed.

    def modified(self, obj):
        return self._session.is_modified(obj)

    def dirty(self, obj):
        return self.modified(obj)

    def new(self, object_type, *args, **kwargs):
        """Creates a new object of the specified type,
        initialized with the specified values, but does not
        save it to the database.

        Note that until the object is saved, its primary
        key may be set directly, but generally the primary
        key will be generated via a sequence or other
        lower-level handler.

        """
        obj = broom.types.get(object_type)(*args, **kwargs)
        obj._db = self
        return obj

    def exists(self, object_type, *object_id):
        """Returns True if the object exists, or False otherwise.

        """
        raise NotImplementedError()

    def refresh(self, obj):
        self.db._session.refresh(obj)

    def read(self, object_type, *object_id):
        with self.transaction():
            return self._read(object_type, *object_id)

    def _read(self, object_type, *object_id):
        """Returns the object identified by the given
        object_id.

        """
        object_type = broom.types.get(object_type)
        obj = self.query(object_type).get(object_id)
        if not obj:
            raise BroomDBObjectNotFoundError(
                "%s with pk=(%s) not found in database"
                    % (object_type.__name__,
                        ",".join([str(i) for i in object_id])
                        )
                    )
        return obj

    def read_safe(self, object_type, *object_id):
        try:
            return self.read(object_type, *object_id)
        except BroomDBObjectNotFoundError:
            pass
        return None

    def read_many(self, object_type, object_ids):
        """Returns a list of objects of the specified
        type matching the provided IDs.  The
        ordering of the returned objects is non-
        deterministic.

        Any objects not found are excluded from
        the return list.

        """
        raise NotImplementedError()

    def read_ordered(self, object_type, object_ids):
        """Returns a list of objects of the specified
        type matching the provided object IDs.

        Results are returned in the same order as the object
        IDs specified.  If an object with a given object_id
        is not found, the None value is set in its
        corresponding position in the return list.

        """
        object_type = broom.types.get(object_type)
        if not isinstance(object_ids, (list,tuple)):
            raise RuntimeError("object_ids must be a list or tuple")
        objects_by_id = {}
        for obj in self.read_many(object_type, object_ids):
            objects_by_id[obj.id] = obj
        ret = []
        for object_id in object_ids:
            ret.append(objects_by_id.get(object_id))
        return ret

    def commit(self):
        if self._transactionContext:
            raise BroomDBClientError("You cannot commit inside a BroomDBTransaction.")
        self._session.commit()

    def rollback(self):
        if self._transactionContext:
            raise BroomDBTransactionAborted()
        self._session.rollback()

    def write(self):
        """Commits all current changes to the database,
        unless a transaction is pending, in which case
        this is a no-op.

        """
        # TODO: This is not real intension here.  Will be replaced 
        #       soon by proper object-level writes. For now we
        #       punt to the commit method.
        self.commit()

    def _write(self, obj):
        """Writes the object to the database.

        If the object is new, a record will be
        created, possibly with an autogenerated
        primary key (depending on the table
        design).

        If the object already exists, it is
        updated.

        """
        # FIXME: Unfortunately sqlalchemy picks up
        #        every change to an existing object,
        #        even if it is not 'saved'.  That is,
        #        until we add a higher-level 
        #        instrumentation, database writes
        #        are 'all-or-none'.
        raise NotImplementedError("Writes are enabled only at the session level.")

    def delete(self, obj):
        """Deletes the object from the database
        as long as no constraints are prevent us
        from doing so.

        """
        self._session.delete(obj)

    def delete_by_id(self, object_type, *object_id):
        object_type = broom.types.get(object_type)
        obj = broom.db.read(object_type, *object_id)
        self._session.delete(obj)
        return

    def delete_many(self, object_type, object_filter):
        """Deletes all of the objects identified
        by the filter as long as all such objects
        can be deleted without violating any
        constraints.

        Otherwise nothing is deleted.

        """
        raise NotImplementedError()

    def transaction(self, *args, **kwargs):
        """Begins a new transaction.  Any writes or deletes
        issued during the transaction will be reverted if
        the transaction is rolled-back or if an exception
        is thrown.

        """
        return BroomDBTransaction(self)

    def _query(self, *args, **kwargs):
        return self._session.query(*args, **kwargs)

    def query(self, *object_types, **kwargs):
        object_types = [broom.types.get(t) for t in object_types]
        query = self._query(*object_types, **kwargs)
        return query

    def _find_by(self, object_type, **kwargs):
        object_type = broom.types.get(object_type)
        filters = []
        for k,vs in kwargs.items():
            f = getattr(object_type, k)
            vs = [vs] if not isinstance(vs, (list,tuple,set)) else list(vs)
            filters.append(broom.or_(f.in_(vs)))
        query = self.query(object_type)
        where = broom.and_(*filters)
        return query.filter(where)

    def find_by(self, object_type, **kwargs):
        with self.transaction():
            return self._find_by(object_type, **kwargs).all()

    def find_one_by(self, object_type, **kwargs):
        with self.transaction():
            try:
                return self._find_by(object_type, **kwargs).one()
            except:
                pass

    def _find(self, object_type, *args, **kwargs):
        return self.query(object_type).filter(*args, **kwargs)

    def find(self, object_type, *args, **kwargs):
        with self.transaction():
            return self._find(object_type, *args, **kwargs).all()

    def find_one(self, object_type, *args, **kwargs):
        with self.transaction():
            return self._find(object_type, *args, **kwargs).one()

    def execute(self, statement):
        """Execute a SQL statement against the database
        directly.

        """
        return self._execute(statement)

    # TODO: Eliminate this and use execute() directly.
    def _execute(self, statement):
        return self._session.execute(statement)

    def _merge(self, obj):
        if obj in self._session:
            self._session.expunge(obj)
        obj = self._session.merge(obj)
        return obj

    # EXPERIMENTAL: DIRECT CONNECTIONS
    def _connection(self):
        return self._engine.connect()

    # EXPERIMENTAL: NOTIFICATIONS
    def _listen(self, callback, object_type, object_id=None):
        # TODO: Figure out the right level of granularity here.
        # connection = self._connection()
        # cursor = connection.cursor()
        # cursor.execute("LISTEN test;")
        # connection.notifies
        pass

    def ddl(self, object_type=None):
        if object_type:
            object_type = broom.types.get(object_type)
            return str(CreateTable(broom.types.get(object_type).__table__).compile(self.engine))
        ddl_ = []
        def dump(sql, *args, **kwargs):
            ddl_.append(sql.compile(dialect=engine.dialect))
        engine = create_engine("postgresql://",
                               strategy="mock",
                               executor=dump
                               )
        broom.BroomObject.metadata.create_all(engine, checkfirst=False)
        return "\n".join(str(x) for x in ddl_)

class _BroomDBListener(object):
    """A listener is responsible for monitoring and processing
    events received from a database matching a topic and
    content of interest.

    """
    def __init__(self, channel, callback=None, interest=None):
        self.channel = channel
        # TODO: We may want to allow multiple callbacks,
        #       differentiated by interest, on the same
        #       listener.

        # Callback:  def callback(channel, interest)
        self.callback = callback
        self.interest = interest

    def isOfInterest(self, payload):
        """Returns True if the payload received via the
        specified channel is of interest to the user.

        """
        return self.interest(payload)

    def onNotify(self, payload):
        if self.isOfInterest(payload):
            return self.callback(self.channel, payload)

# Payload can be:  
#    {'object_type': <broom.types.<type>.__class__.__name__>,
#     'object_id': <PK for object whose database value changed>,
#     'action': [insert|update|delete],
#     'fields': [list of fields changed on update]
#    }
# With this, a client can then identify any in-memory, valid
# fields and invalidate them, forcing invalidation up the
# dependency tree.
#
# In this way, for example, a selector can keep a ConfigSet
# (on graph) in memory, but subscribe to changes to any
# selector-related config or dependency changes.  The first
# time the selector is evaluated data is loaded and code
# executed.  But the next time this will be cached, and the
# load (and possibly calculation) will not need to be done.
#
# But if a row changes that affects that, the server can
# pick up that notification, identify which fields (nodes)
# have changed, and invalidate them.  In this way we only
# have to reload and recalculate what we need to, and only 
# when we need to.

def _BroomDBInterest(object):

    def __init__(self, object_type, object_id=None):
        self.object_type = self.object_type.__class__.__name__
        self.object_id = object_id

    def __call__(self, payload):
        payload = json.loads(payload)
        if payload['object_type'] != self.object_type:
            return False
        if self.object_id is not None \
                and payload['object_id'] != self.object_id:
            return False
        return True

class BroomDBSession(object):

    def __init__(self, db):
        self._db = db

    @property
    def db(self):
        return self._db

    def __enter__(self):
        if self.db._session:
            self._session = self.db._session
            self.db._session = self.db._Session()
        self.db._session._db = self.db

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.db._session.close()
        finally:
            self.db._session = self._session

class BroomDBTransaction(object):

    def __init__(self, db):
        self._db = db

    @property
    def db(self):
        return self._db

    def __enter__(self):
        if self.db._transactionContext:
            raise RuntimeError("Nested transactions are not yet supported.")
        self.db.commit()
        self.db._transactionContext = self
        # TODO: We explicitly commit any open transaction here,
        #       but long-term we want either a nested transaction
        #       or a move to our own session management.

    def __exit__(self, exc_type, exc_value, trackback):
        self.db._transactionContext = None
        self.db.commit() if not exc_type else self.db.rollback()
