import broom

class SelectorField(broom.BroomObject):

    __tablename__ = 'selector_field'
    __table_args__ = (
            broom.UniqueConstraint("name"),
            )

    selector_field_id = broom.Serial(__tablename__, primary_key=True)
    name = broom.Column(broom.String, nullable=False)
    weight = broom.Column(broom.Integer, nullable=False)

    ID = broom.stored('selector_field_id')
    Name = broom.stored('name')
    Weight = broom.stored('weight')
