import broom
import itertools

class SelectorNode(broom.BroomObject):

    __tablename__ = 'selector_node'

    selector_node_id = broom.Serial(__tablename__, primary_key=True)
    selector_node_type = broom.Column(broom.String, broom.ForeignKey("val_selector_node_type.selector_node_type"), nullable=False)
    parent_selector_node_id = broom.Column(broom.Integer, broom.ForeignKey("selector_node.selector_node_id"))

    selector = broom.relationship("Selector", back_populates="root_node")
    parent_node = broom.relationship("SelectorNode", back_populates="child_nodes", remote_side=[selector_node_id])
    child_nodes = broom.relationship("SelectorNode", back_populates="parent_node")

    node_type = broom.relationship("SelectorNodeType")

    __mapper_args__ = {
            'polymorphic_on': selector_node_type,
            'with_polymorphic': '*'
            }

    ID = broom.stored('selector_node_id')
    Type = broom.stored('selector_node_type')
    _Children = broom.stored('child_nodes')

    @broom.field
    def Children(self):
        return [c.RootNode()
                    if isinstance(c, broom.types.Selector)
                    else c
                for c in self._Children()]


    @broom.field
    def IsExpression(self):
        return self.Type() == 'expression'

    @broom.field
    def IsLeafNode(self):
        return not self.Children()

    def evaluate(self, selector, objs):
        raise NotImplementedError()

    def __repr__(self):
        return '%s(Children=%s)' % (self.__class__.__name__, self.Children())

class SelectorEquals(SelectorNode):

    # TODO: All expressions are equals, so we should update the table
    #       name to reflect this.
    __tablename__ = 'selector_node_expression'

    selector_node_id = broom.Column(broom.Integer, broom.ForeignKey("selector_node.selector_node_id"), primary_key=True)
    selector_field_id = broom.Column(broom.Integer, broom.ForeignKey("selector_field.selector_field_id"))
    value = broom.Column(broom.String)

    selector_field = broom.relationship("SelectorField", uselist=False)

    # TODO: The node type value (and thus identity value set in 
    #       __mapper_args__) should be 'equals'.
    __mapper_args__ = {
            'polymorphic_identity': 'expression'
            }

    Field = broom.stored('selector_field')
    Value = broom.stored('value')

    @broom.field
    def Key(self):
        if self.Field():
            return self.Field().Name()

    def evaluate(self, selector, objs):
        ret = set()
        for obj in objs:
            if getattr(obj, self.Key()) != self.Value():
                continue

            # TODO: Consider using descriptors to allow for update-
            #       by-reference while still invalidating the graph.
            attractions = selector.AttractionByObject()
            attractions[obj].update(self.Field())
            selector.AttractionByObject = attractions
            ret.add(obj)
        return ret

    def __repr__(self):
        return '%s(Key=%s, Value=%s)' % (self.__class__.__name__, self.Key(), self.Value())

class SelectorNull(SelectorNode):

    __mapper_args__ = {
            'polymorphic_identity': 'null'
            }

    def evaluate(self, selector, objs):
        return self.Children()[0].evaluate(selector, objs)

class SelectorIntersect(SelectorNode):

    __mapper_args__ = {
            'polymorphic_identity': 'intersection'
            }

    def evaluate(self, selector, objs):
        for child in self.Children():
            objs = objs.intersection(child.evaluate(selector, objs))
        return objs

class SelectorUnion(SelectorNode):

    __mapper_args__ = {
            'polymorphic_identity': 'union'
            }

    def evaluate(self, selector, objs):
        return set(itertools.chain(*[child.evaluate(selector, objs) for child in self.Children()]))

