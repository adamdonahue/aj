import broom

class ACEHostFilterAddrgroupNetblockCollection(broom.BroomObject):

    __tablename__ = 'ace_host_filter_addrgroup_netblock_collection'

    ace_host_filter_id = broom.Column(broom.Integer, broom.ForeignKey("ace_host_filter_addrgroup.ace_host_filter_id"), primary_key=True)
    netblock_collection_id = broom.Column(broom.Integer, broom.ForeignKey("jazzhands.netblock_collection.netblock_collection_id"), primary_key=True)
    order_in_filter = broom.Column(broom.Integer, nullable=False)

    ace_host_filter_addrgroup = broom.relationship('ACEHostFilterAddrgroup')
    netblock_collection = broom.relationship("NetblockCollection")

    ACEHostFilterAddrgroup = broom.stored('ace_host_filter_addrgroup')
    NetblockCollection = broom.stored('netblock_collection')
