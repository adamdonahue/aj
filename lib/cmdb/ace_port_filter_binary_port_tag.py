import broom

class ACEPortFilterBinaryPortTag(broom.BroomObject):

    __tablename__ = 'ace_port_filter_binary_port_tag'

    ace_port_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_port_filter_binary.ace_port_filter_id"), primary_key=True, autoincrement=False)
    port_tag = broom.Column(broom.String, primary_key=True, nullable=False)

    ace_port_filter = broom.relationship("ACEPortFilterBinary", back_populates="tags")

    ID = broom.stored('ace_port_filter_id')
    Tag = broom.stored('port_tag')

    @broom.field
    def Ports(self):
        raise NotImplementedError("Need to map tag names to port number(s).")
