"""BroomObject types registry.

Serves two purposes:

    * Lists BroomObject classes that are persistable.  Although not
      strictly required at this juncture, can be used as a sanity
      check and point of control should other users wish to develop
      and persist objects using the BroomObject model.
    * Provides a simple, global namespace for access to BroomObject
      classes.

      Rather than having to import each module containing the
      classes a user wishes to develop, he can now simply
      import broom and refer to the classes by name via the
      types variable, e.g.,

          import broom

          broom.types.Service (loads cmdb.service.Service)
          broom.types.Selector (loads cmdb.selector.Selector)

      This also provides a lightweight means of ensuring we keep
      a single class per 'thing', or at least a way of seeing
      what kind of classes we have out there.

"""
import importlib
import inspect

registry = [
        ('Selector', 'cmdb.selector'),
        ('SelectorSet', 'cmdb.selector_set'),
        ('SelectorField', 'cmdb.selector_field'),
        ('SelectorNode', 'cmdb.selector_node'),
        ('SelectorEquals', 'cmdb.selector_node'),
        ('SelectorIntersect', 'cmdb.selector_node'),
        ('SelectorUnion', 'cmdb.selector_node'),
        ('SelectorNull', 'cmdb.selector_node'),
        ('SelectorNodeType', 'cmdb.val_selector_node_type'),
        ('Service', 'cmdb.service'),
        ('ServiceInstantiation', 'cmdb.service_instantiation'),
        ('ServiceEndpoint', 'cmdb.service_instantiation_endpoint'),
    ]

class types(object):
    """Dynamic type loader."""

    def __init__(self):
        self.typeMap = {}
        self.modules = {}
        self.types = {}
        for c, m in registry:
            if c in self.typeMap:
                raise RuntimeError("Type %s is defined more than once." % c)
            self.typeMap[c] = m

    def __getattr__(self, k):
        return self.get(k)

    def get(self, k):
        if k not in self.types:
            self.types[k] = self.load_type(k)
        return self.types[k]

    def load_type(self, k):
        if inspect.isclass(k):
            k = k.__name__
        if self.typeMap[k] not in self.modules:
            self.modules[k] = importlib.import_module(self.typeMap[k])
        return getattr(self.modules[k], k)

    def preload(self):
        for c in self.typeMap:
            if c in self.types:
                continue
            self.types[c] = self.load_type(c)

types = types()
