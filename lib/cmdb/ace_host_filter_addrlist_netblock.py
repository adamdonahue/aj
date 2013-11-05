import broom

class ACEHostFilterAddrlistNetblock(broom.BroomObject):

    __tablename__ = 'ace_host_filter_addrlist_netblock'

    ace_host_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_host_filter_addrlist.ace_host_filter_id"), primary_key=True)
    netblock_id = broom.Column(broom.Integer, broom.ForeignKey("jazzhands.netblock.netblock_id"), primary_key=True)
    order_in_filter = broom.Column(broom.Integer, nullable=False)

    ace_host_filter_addrlist = broom.relationship('ACEHostFilterAddrlist')
    netblock = broom.relationship("Netblock")


    ACEHostFilterAddrlist = broom.stored('ace_host_filter_addrlist')
    Netblock = broom.stored('netblock')
    OrderInFilter = broom.stored('order_in_filter')
