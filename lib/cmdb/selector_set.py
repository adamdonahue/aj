"""

Test: cmdb.tests.selector
"""

import broom

class SelectorSet(broom.BroomObject):
    """A collection of selectors that, when evaluated, assigns
    each object to the selectors it matched and the strength-
    by which it matched.

    """
    @broom.field(broom.Settable)
    def SelectorObjects(self):
        return []

    @broom.field
    def SelectorObjectsByName(self):
        return dict([(s.Name(),s) for s in self.SelectorObjects()])

    @broom.field
    def SelectorObject(self, name):
        return self.SelectorObjectsByName().get(name)

    def evaluate(self, objs):
        attractions = []
        for s in self.SelectorObjects():
            for o,sa in s.evaluate(objs):
                attractions.append((o,sa))
        return list(reversed(sorted(attractions)))

    def evaluateOne(self, obj):
        return [a for o,a in self.evaluate([obj])]

