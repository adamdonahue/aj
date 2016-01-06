"""Selectors.

Test: cmdb.tests.selector

"""

import collections
import broom
import itertools

class SelectorAttraction(broom.BroomObject):
    """An object selected by a given selector instance is
    "attracted" to that instance with a given strength.

    This attraction is used to resolve variable conflicts
    when multiple selectors assign different values
    to the same object.

    """
    @broom.field(broom.Settable)
    def SelectorObject(self):
        return None

    @broom.field(broom.Settable)
    def FieldsByWeight(self):
        return {}

    # XXX --- broom stored migration --- look at this!
    def update(self, field):
        fieldsByWeight = self.FieldsByWeight()
        fieldsByWeight.setdefault(field.Weight(), []).append(field)
        self.FieldsByWeight = fieldsByWeight

    @broom.field
    def Strength(self):
        """The strength of a (selector, object) pair is how
        closely the selector matches the object.  We use this
        to resolve conflicts.

        At the moment strength is an object that essentially
        has meaning only in comparison to other such objects.
        There is no real meaning outside of that, just as
        a number on its own is really meaningless outside
        its implicit relationship as a means of comparison
        to other numbers (speaking orderinally or cardinally).

        That said, we determine strength as function of
        these two things:

           How strongly a field matches an object (its weight).
           How specific the overall selector is itself.

        The weight is merely a function of the fields that matched
        the object.  The higher the weight, but more tightly
        an object is attracted to the selector.

        But this is not enough, because clearly, if I have two
        fields with the same weights

            name    weight
            ----    ------
            A       1
            B       1

        and I define two selectors

            name     logic          config
            ----     -----          ------
            S        A = 1 & B = 2  {'x': 'y'}
            T        B = 2          {'x': 'z'}

        clearly an object with settings A = 1 and B = 2 will
        match both and will match both with weight one.

        Yet it seems obvious that the more specific match would
        be selector S, not selector T.  So we can't just use

        weights alone.  We need to define some other notion of
        selectiveness.

        We therefore measure strength as the number of fields
        that match at a given weight.

        Reapplying this logic, then, if we apply the above
        selectors to the same object we now unambigiously
        resolve to the S selector, and pick up the value
        there with no conflict.

        But what if the weights are different?  What if we
        have

            name    weight
            ----    ------
            A       1
            B       2

        with the same selectors?  The object with A = 1 and
        B = 2 still matches both, this time with weight two.
        But it matches only one field at this weight in both
        selectors.  So the final algorithm is that when the
        count of fields matched of a certain weight are equal,
        we move down to the next set of weighted fields and
        compare their counts, etc., until we have either
        exhausted all levels (a potential conflict), or have
        determined a selector that attracts an instance more
        strongly.

        """
        return list(reversed(sorted([(w,len(fs)) for w,fs in self.FieldsByWeight().items()])))

    def __eq__(self, other):
        return self.Strength() == other.Strength()

    def __gt__(self, other):
        return self.Strength() > other.Strength()

class Selector(broom.BroomObject):

    __tablename__ = 'selector'
    __table_args__ = (
            broom.UniqueConstraint("name"),
            )

    selector_id = broom.Serial(__tablename__, primary_key=True)
    name = broom.Column(broom.String, nullable=False)
    root_node_id = broom.Column(broom.Integer, broom.ForeignKey("selector_node.selector_node_id"), nullable=False)

    root_node = broom.relationship("SelectorNode", back_populates="selector")
    selector_service_instantiations = broom.relationship("SelectorServiceInstantiation", back_populates="selector")

    class _HashableDict(object):
        """Wrapper for normally unhashable dictionaries.

        """
        def __init__(self, unhashable):
            self._unhashable = unhashable

        get = dict.get

        @property
        def unhashable(self):
            return self._unhashable

        def __getattr__(self, n):
            return self.unhashable.get(n)

    ID = broom.stored('selector_id')
    Name = broom.stored('name')
    RootNode = broom.stored('root_node')
    SelectorServiceInstantiations = broom.stored('selector_service_instantiations')

    @broom.field
    def Children(self):
        return [self.RootNode()]

    @broom.field(broom.Settable)
    def AttractionByObject(self):
        return collections.defaultdict(lambda: SelectorAttraction(SelectorObject=self))

    def hashable(self, o):
        if isinstance(o, dict):
            return self._HashableDict(o)
        return o

    def evaluate(self, objs):
        if not objs:
            return []
        objs = self.RootNode().evaluate(self,
                                        set([self.hashable(o) for o in objs])
                                        )
        return [(obj.unhashable
                    if isinstance(obj, self._HashableDict)
                        else obj,
                 self.AttractionByObject()[obj])
                    for obj in objs]

    def evaluateOne(self, obj):
        res = self.evaluate([obj])
        if not res:
            return None
        obj, attraction = res[0]
        return attraction

    @broom.field
    def ServiceInstantiationsByRole(self):
        return dict((obj.Role(), obj) for obj in self.SelectorServiceInstantiations())
