import broom

class SelectorNodeType(broom.BroomObject):

    __tablename__ = 'val_selector_node_type'
    __table_args__ = (
            broom.CheckConstraint("max_children IS NULL or min_children <= max_children"),
            )

    selector_node_type = broom.Column(broom.String, primary_key=True)
    min_children = broom.Column(broom.Integer, broom.CheckConstraint("min_children >= 0"), nullable=False, server_default=broom.text("0"))
    max_children = broom.Column(broom.Integer)

    Type = broom.stored('selector_node_type')
    MinChildren = broom.stored('min_children')
    MaxChildren = broom.stored('max_children')
