import broom
from  sqlalchemy.ext.hybrid import hybrid_property

class ACEPortFilter(broom.BroomObject):

    __tablename__ = 'ace_port_filter'
    __table_args__ = (
            broom.UniqueConstraint("ace_port_filter_id", "operation"),
            broom.UniqueConstraint("ace_id", "ace_side"),
            broom.ForeignKeyConstraint(["ace_id",     "ace_protocol"],
                                       ["ace.ace_id", "ace.protocol"]
                                     ),
            )

    ace_port_filter_id = broom.Serial(__tablename__, primary_key=True)
    ace_id = broom.Column(broom.Integer, nullable=False)
    ace_protocol = broom.Column(broom.String(3), broom.CheckConstraint("ace_protocol IN ('udp', 'tcp')"), nullable=False)
    ace_side = broom.Column(broom.String(6), broom.CheckConstraint("ace_side IN ('source', 'dest')"), nullable=False)
    operation = broom.Column(broom.String(5), broom.CheckConstraint("operation IN ('eq', 'lt', 'gt', 'neq', 'range')"), nullable=False, server_default=broom.text("'eq'"))

    ace = broom.relationship("ACE", back_populates="ace_port_filters")

    category = broom.column_property(broom.case(value=operation, whens=[("range", "range")], else_="binary"))

    __mapper_args__ = {
            'polymorphic_on': category,
            'with_polymorphic': '*'
            }

    ID = broom.stored('ace_port_filter_id')
    Protocol = broom.stored('ace_protocol')
    Side = broom.stored('ace_side')
    Operation = broom.stored('operation')
    Category = broom.stored('category')
    ACE = broom.stored('ace')

class ACEPortFilterBinary(ACEPortFilter):

    __tablename__ = 'ace_port_filter_binary'

    ace_port_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_port_filter.ace_port_filter_id"), primary_key=True)
    operation = broom.Column(broom.String(5), broom.CheckConstraint("operation IN ('eq', 'lt', 'gt', 'neq')"), nullable=False)

    __mapper_args__ = {
            'polymorphic_identity': 'binary'
            }

    entries = broom.relationship("ACEPortFilterBinaryEntry", order_by="ACEPortFilterBinaryEntry.order_in_filter")

    Entries = broom.stored('entries')

    @broom.field
    def AllPorts(self):
        raise NotImplementedError("Return union of Ports(), Tags() port "
                                  "numbers, and expanded Ranges()"
                                  )

    @broom.field
    def _CiscoFormat(self):
        return " ".join([
            self.Operation(),
            ",".join([e._CiscoFormat() for e in self.Entries()])
            ])

class ACEPortFilterRange(ACEPortFilter):

    __tablename__ = 'ace_port_filter_range'
    __table_args__ = (
            broom.CheckConstraint("start_port <= end_port"),
            )

    ace_port_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_port_filter.ace_port_filter_id"), primary_key=True)
    operation = broom.Column(broom.String(5), nullable=False)
    start_port = broom.Column(broom.Integer, nullable=False)
    end_port = broom.Column(broom.Integer, nullable=False)

    __mapper_args__ = {
            'polymorphic_identity': 'range'
            }

    StartPort = broom.stored('start_port')
    EndPort = broom.stored('end_port')

    @broom.field
    def Ports(self):
        return range(self.start_port, self.end_port + 1)

    @broom.field
    def AllPorts(self):
        return self.Ports()

    @broom.field
    def Tags(self):
        return []

    @broom.field
    def _CiscoFormat(self):
        return " ".join([self.Operation(),
                         str(self.StartPort()),
                         str(self.EndPort())
                         ])
