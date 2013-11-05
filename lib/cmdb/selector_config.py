import broom

# TODO: Use this in the future to generalize the notion
#       of a config, allowing selector users to leverage
#       it.

class SelectorConfigException(Exception):
    pass

class SelectorConfig(broom.BroomObject):
    """Associates a selector with a configuration."""

    @broom.field(broom.Settable)
    def Selector(self):
        return None

    @broom.field(broom.Settable)
    def Config(self):
        return {}

class SelectorConfigSet(broom.BroomObject):
    """Associates each of a set of selectors with a dictionary of
    key/value pairs, and uses object-to-selector weightings
    to resolve key conflicts where possible.

    """

    @broom.field(broom.Settable)
    def SelectorObjects(self):
        """Selectors to evaluate against one or more
        objects.

        """
        return []

    @broom.field
    def SelectorSet(self):
        return broom.types.SelectorSet(SelectorObjects=self.SelectorObjects())

    # TODO: Put on the graph after handling non-hashable args.
    # TODO: Rename this to reflect service_instantiation as 'config'.
    def objectConfigs(self, objs):
        return [(obj, self.objectConfig(obj)) for obj in objs]

    # TODO: Put on the graph after handling non-hashable args.
    # TODO: Rename this to reflect service_instantiation as 'config'.
    def objectConfig(self, obj):
        """Returns the resolved configuration for the object.

        """
        attractions = self.SelectorSet().evaluateOne(obj)
        selectors = {}
        for a in attractions:
            selectors.setdefault(a, []).append(a.SelectorObject())

        # We then build up the dependencies list by role
        # by fetching the dependencies in priority based
        # on the most closely matching selector.
        ds = {}
        for attraction in attractions:
            t = {}  # s -> r -> si
            for selector in selectors[attraction]:
                for d in selector.SelectorServiceInstantiations():
                    service = d.Service().Name()
                    if d.Role() in ds.get(service, {}):
                        continue
                    if d.Role() in t.get(service, {}):
                        raise SelectorConfigException("ambiguous: % (role=%s)" \
                                % (service, d.Role()))
                    t.setdefault(service, {})[d.Role()] \
                            = d.ServiceInstantiation()
            ds.update(t)
        return ds
