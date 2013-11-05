import broom
from ace_port_filter import ACEPortFilterBinaryPortEntry

class ACEPortFilterBinaryPort(broom.BroomObject):

    __tablename__ = 'ace_port_filter_binary_port'

    ace_port_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_port_filter_binary.ace_port_filter_id"), primary_key=True, autoincrement=False)
    port = broom.Column(broom.Integer, primary_key=True, autoincrement=False)

    ace_port_filter = broom.relationship("ACEPortFilterBinary", back_populates="ports")

    Port = broom.stored('port')
    PortFilter = broom.stored('ace_port_filter')

    @broom.field
    def Ports(self):
        return [self.Port()]



