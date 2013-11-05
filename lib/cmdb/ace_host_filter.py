import broom
import itertools

class ACEHostFilter(broom.BroomObject):

    __tablename__ = 'ace_host_filter'
    __table_args__ = (
            broom.UniqueConstraint("ace_host_filter_id", "host_filter_type"),
            broom.UniqueConstraint("ace_id", "ace_side")
            )

    ace_host_filter_id = broom.Serial(__tablename__, primary_key=True)
    ace_id = broom.Column(broom.Integer, broom.ForeignKey("ace.ace_id"), nullable=False)
    ace_side = broom.Column(broom.String(6), broom.CheckConstraint("ace_side IN ('source', 'dest')"), nullable=False)
    host_filter_type = broom.Column(broom.String(9), broom.CheckConstraint("host_filter_type IN ('addr', 'addrlist', 'addrgroup')"), nullable=False)

    ace = broom.relationship("ACE", back_populates="ace_host_filters")

    __mapper_args__ = {
            'polymorphic_on': host_filter_type,
            'with_polymorphic': '*'
            }

    ID = broom.stored('ace_host_filter_id')
    Side = broom.stored('ace_side')
    Type = broom.stored('host_filter_type')
    ACE = broom.stored('ace')

    @broom.field
    def PortFilter(self):
        return self.ACE()._PortFiltersBySide().get(self.Side())


class ACEHostFilterAddr(ACEHostFilter):

    __tablename__ = 'ace_host_filter_addr'

    ace_host_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_host_filter.ace_host_filter_id"), primary_key=True)
    host_filter_type = broom.Column(broom.String(9), broom.CheckConstraint("host_filter_type = 'addr'"), nullable=False, server_default=broom.text("'addr'"))
    netblock_id = broom.Column(broom.Integer, broom.ForeignKey("jazzhands.netblock.netblock_id"), nullable=False)

    netblock = broom.relationship("Netblock")

    __mapper_args__ = {
            'polymorphic_identity': 'addr'
            }

    Netblock = broom.stored('netblock')

    @broom.field
    def IsHost(self):
        return self.Netblock().IsSingleAddress()

    @broom.field
    def IsAny(self):
        return self.Netblock().IPAddress() == '0.0.0.0/0'

    @broom.field
    def IP(self):
        return self.Netblock().Host()

    @broom.field
    def Hostmask(self):
        return self.Netblock().Hostmask()

    @broom.field
    def Netmask(self):
        return self.Netblock().Netmask()

    @broom.field
    def _CiscoFormat(self):
        if self.IsAny():
            hostFilter = 'any'
        elif self.IsHost():
            hostFilter = 'host ' + self.IP()
        else:
            hostFilter = ' '.join([self.IP(), self.Hostmask()])
        portFilter = (' ' + self.PortFilter()._CiscoFormat()) \
            if self.PortFilter() \
                else ''
        return hostFilter + portFilter

class ACEHostFilterAddrlist(ACEHostFilter):

    __tablename__ = 'ace_host_filter_addrlist'

    ace_host_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_host_filter.ace_host_filter_id"), primary_key=True)
    host_filter_type = broom.Column(broom.String(9), broom.CheckConstraint("host_filter_type = 'addrlist'"), nullable=False, server_default=broom.text("'addrlist'"))

    ace_host_filter_addrlist_netblocks = broom.relationship("ACEHostFilterAddrlistNetblock", order_by="ACEHostFilterAddrlistNetblock.order_in_filter")

    __mapper_args__ = {
            'polymorphic_identity': 'addrlist'
            }

    _NetblockRefs = broom.stored('ace_host_filter_addrlist_netblocks')

    @broom.field
    def Netblocks(self):
        return [x.Netblock() for x in self._NetblockRefs()]

    @broom.field
    def _CiscoFormat(self):
        hostFilter = "addrlist " + ",".join([n.Text() for n in self.Netblocks()])
        portFilter = (' ' + self.PortFilter()._CiscoFormat()) \
                if self.PortFilter() \
                    else ''
        return hostFilter + portFilter

class ACEHostFilterAddrgroup(ACEHostFilter):

    __tablename__ = 'ace_host_filter_addrgroup'

    ace_host_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_host_filter.ace_host_filter_id"), primary_key=True)
    host_filter_type = broom.Column(broom.String(9), broom.CheckConstraint("host_filter_type = 'addrgroup'"), nullable=False, server_default=broom.text("'addrgroup'"))

    ace_host_filter_addrgroup_netblock_collections = broom.relationship("ACEHostFilterAddrgroupNetblockCollection", order_by="ACEHostFilterAddrgroupNetblockCollection.order_in_filter")

    __mapper_args__ = {
            'polymorphic_identity': 'addrgroup'
            }

    _NetblockCollectionRefs = broom.stored('ace_host_filter_addrgroup_netblock_collections')

    @broom.field
    def NetblockCollections(self):
        return [x.NetblockCollection() for x in self._NetblockCollectionRefs()]

    @broom.field
    def NetblockCollectionsByName(self):
        return dict((c.Name(), c) for c in self.NetblockCollections())

    @broom.field
    def Netblocks(self):
        netblocks = list(set(itertools.chain(*[c.Netblocks() for c in self.NetblockCollections()])))
        return netblocks

    @broom.field
    def _CiscoFormat(self):
        hostFilter = "addrgroup " + ",".join(c.Name() for c in self.NetblockCollections())
        portFilter = (' ' + self.PortFilter()._CiscoFormat()) \
                if self.PortFilter() \
                    else ''
        return hostFilter + portFilter


