import broom

class ACEPortFilterBinaryPortRange(broom.BroomObject):

    __tablename__ = 'ace_port_filter_binary_port_range'

    ace_port_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_port_filter_binary.ace_port_filter_id"), primary_key=True, autoincrement=False)
    start_port = broom.Column(broom.Integer, primary_key=True, autoincrement=False)
    end_port = broom.Column(broom.Integer, primary_key=True, autoincrement=False)

    ace_port_filter = broom.relationship("ACEPortFilterBinary", back_populates="ranges")

    StartPort = broom.stored('start_port')
    EndPort = broom.stored('end_port')
    PortFilter = broom.stored('ace_port_filter')

    @broom.field
    def Ports(self):
        return range(self.StartPort(), self.EndPort() + 1)
