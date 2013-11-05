import broom

class ACEBase(broom.BroomObject):

    __tablename__ = 'ace_base'
    __table_args__ = (
            broom.UniqueConstraint("ace_id", "ace_type"),
            )

    ace_id = broom.Serial("ace_id", primary_key=True)
    acl_id = broom.Column(broom.Integer, broom.ForeignKey("acl.acl_id"), nullable=False)
    ace_type = broom.Column(broom.String, nullable=False)
    order_in_acl = broom.Column(broom.Integer, nullable=False)
    as_extracted = broom.Column(broom.String)
    acl = broom.relationship("ACL", back_populates="aces")

    category = broom.column_property(broom.case(value=ace_type, whens=[("remark", "remark")], else_="rule"))

    __mapper_args__ = {
            'polymorphic_on': category,
            'with_polymorphic': '*'
            }

    ID = broom.stored('ace_id')
    Type = broom.stored('ace_type')
    ACL = broom.stored('acl')
    _AsExtracted = broom.stored('as_extracted')
    OrderInACL = broom.stored('order_in_acl')

    @broom.field
    def _MatchesCloudAPI(self):
        return self._CiscoFormat() == self._AsExtracted()

class ACE(ACEBase):

    __tablename__ = 'ace'
    __table_args__ = (
            broom.UniqueConstraint("ace_id", "protocol"),
            )

    ace_id = broom.Column(broom.Integer, broom.ForeignKey("ace_base.ace_id"), primary_key=True)
    ace_type = broom.Column(broom.String, broom.CheckConstraint("ace_type IN ('permit', 'deny')"), nullable=False)
    protocol = broom.Column(broom.String(3), broom.CheckConstraint("protocol IN ('ip', 'tcp', 'udp', 'icmp', 'esp')"), nullable=False)
    extra = broom.Column(broom.String)

    __mapper_args__ = {
            'polymorphic_identity': 'rule'
            }

    # TODO: Can we more easily have dest/source separation here?
    ace_host_filters = broom.relationship("ACEHostFilter", back_populates="ace")

    # TODO: Probably subclass ACE and link port filters to it, or link
    #       port filters to host filters.
    # TODO: Can we more easily have dest/source separation here?
    ace_port_filters = broom.relationship("ACEPortFilter", back_populates="ace")

    _HostFilters = broom.stored('ace_host_filters')

    @broom.field
    def _HostFiltersBySide(self):
        return dict((f.Side(), f) for f in self._HostFilters())

    _PortFilters = broom.stored('ace_port_filters')

    @broom.field
    def _PortFiltersBySide(self):
        portFilters = self._PortFilters()
        if not portFilters:
            return {}
        return dict((f.Side(), f) for f in self._PortFilters())

    @broom.field
    def SourceHostFilter(self):
        return self._HostFiltersBySide()['source']

    @broom.field
    def SourcePortFilter(self):
        return self._PortFiltersBySide().get('source', None)

    @broom.field
    def DestHostFilter(self):
        return self._HostFiltersBySide()['dest']

    @broom.field
    def DestPortFilter(self):
        return self._PortFiltersBySide().get('dest', None)

    @broom.field
    def Permit(self):
        return self.Type() == 'permit'

    @broom.field
    def Deny(self):
        return self.Type() == 'deny'

    Protocol = broom.stored('protocol')
    _Extra = broom.stored('extra')

    @broom.field
    def _ExtraKeywords(self):
        return self._Extra().split(',') if self._Extra() else []

    @broom.field
    def Established(self):
        return 'established' in self._ExtraKeywords()

    @broom.field
    def _CiscoFormat(self):
        # TODO: Port filter should be part of host filter,
        #       and host filter should probably be just called
        #       filter.
        pieces = [self.Type(),
                  self.Protocol(),
                  self.SourceHostFilter()._CiscoFormat(),
                  self.DestHostFilter()._CiscoFormat()
                  ]
        if self._Extra():
            pieces.append(self._Extra())
        return " ".join(pieces)

class ACERemark(ACEBase):

    __tablename__ = 'ace_remark'

    ace_id = broom.Column(broom.Integer, broom.ForeignKey("ace_base.ace_id"), primary_key=True)
    ace_type = broom.Column(broom.String, broom.CheckConstraint("ace_type in ('remark')"), nullable=False)
    remark = broom.Column(broom.String)
    is_empty_line = broom.Column(broom.Boolean)

    __mapper_args__ = {
            'polymorphic_identity': 'remark'
            }

    IsEmptyLine = broom.stored('is_empty_line')
    _Remark = broom.stored('remark')

    @broom.field
    def Remark(self):
        if self.IsEmptyLine():
            return None
        return self._Remark() or ''

    @broom.field
    def _CiscoFormat(self):
        if self.IsEmptyLine():
            return ''
        return "remark " + self.Remark()
