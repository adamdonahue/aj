import broom

class ConfigVariable(broom.BroomObject):

    __tablename__ = 'config_variable'

    config_variable_id = broom.Serial(__tablename__, primary_key=True)
    name = broom.Column(broom.String, nullable=False)
    data_type = broom.Column(broom.String, broom.CheckConstraint("data_type in ('scalar', 'list', 'map'"), nullable=False, server_default=broom.text("'scalar'"))

    ID = broom.stored('config_variable_id')
    Name = broom.stored('name')
    DataType = broom.stored('data_type')
