import broom

class ACEPortFilterBinaryEntry(broom.BroomObject):

    __tablename__ = 'ace_port_filter_binary_entry'

    ace_port_filter_binary_entry_id = broom.Serial(__tablename__, primary_key=True)
    ace_port_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_port_filter_binary.ace_port_filter_id"))
    order_in_filter = broom.Column(broom.Integer, primary_key=True)
    entry_type = broom.Column(broom.String(10), nullable=False)

    __mapper_args__ = {
            'polymorphic_on': entry_type,
            'with_polymorphic': '*'
            }

    ace_port_filter = broom.relationship("ACEPortFilterBinary")

    ID = broom.stored('ace_port_filter_binary_entry_id')
    OrderInFilter = broom.stored('order_in_filter')
    EntryType = broom.stored('entry_type')
    PortFilter = broom.stored('ace_port_filter')


class ACEPortFilterBinaryPort(ACEPortFilterBinaryEntry):

    __tablename__ = 'ace_port_filter_binary_port'

    ace_port_filter_binary_entry_id = broom.Column(broom.Integer, broom.ForeignKey("ace_port_filter_binary_entry.ace_port_filter_binary_entry_id"), primary_key=True, autoincrement=False)
    port = broom.Column(broom.Integer, primary_key=True, autoincrement=False)
    entry_type = broom.Column(broom.String(10), nullable=False)

    Port = broom.stored('port')

    @broom.field
    def Ports(self):
        return [self.Port()]

    __mapper_args__ = {
            'polymorphic_identity': 'port'
            }

    @broom.field
    def _CiscoFormat(self):
        return '%s' % self.Port()

class ACEPortFilterBinaryPortRange(ACEPortFilterBinaryEntry):

    __tablename__ = 'ace_port_filter_binary_port_range'

    ace_port_filter_binary_entry_id = broom.Column(broom.Integer, broom.ForeignKey("ace_port_filter_binary_entry.ace_port_filter_binary_entry_id"), primary_key=True, autoincrement=False)
    entry_type = broom.Column(broom.String(10), nullable=False)
    start_port = broom.Column(broom.Integer, primary_key=True, autoincrement=False)
    end_port = broom.Column(broom.Integer, primary_key=True, autoincrement=False)

    StartPort = broom.stored('start_port')
    EndPort = broom.stored('end_port')

    @broom.field
    def Ports(self):
        return range(self.StartPort(), self.EndPort() + 1)

    @broom.field
    def _CiscoFormat(self):
        return '%s-%s' % (self.StartPort(), self.EndPort())

    __mapper_args__ = {
            'polymorphic_identity': 'port_range'
            }

class ACEPortFilterBinaryPortTag(ACEPortFilterBinaryEntry):

    __tablename__ = 'ace_port_filter_binary_port_tag'

    ace_port_filter_binary_entry_id = broom.Column(broom.Integer, broom.ForeignKey("ace_port_filter_binary_entry.ace_port_filter_binary_entry_id"), primary_key=True, autoincrement=False)
    entry_type = broom.Column(broom.String(10), nullable=False)
    port_tag = broom.Column(broom.String, primary_key=True, nullable=False)

    Tag = broom.stored('port_tag')

    @broom.field
    def Ports(self):
        raise NotImplementedError("Need to map tag names to port number(s).")

    @broom.field
    def _CiscoFormat(self):
        return self.Tag()

    __mapper_args__ = {
            'polymorphic_identity': 'port_tag'
            }


