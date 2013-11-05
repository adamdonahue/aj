import broom

class ACL(broom.BroomObject):

    __tablename__ = 'acl'
    __table_args__ = (
            broom.ForeignKeyConstraint(['vlan_id', 'datacenter_id'],
                                       ['cloudapi.vlan.id', 'cloudapi.vlan.datacenter_id']
                                     ),
            )

    acl_id = broom.Serial(__tablename__, primary_key=True)
    vlan_id = broom.Column(broom.Integer)
    datacenter_id = broom.Column(broom.String(4))
    aces_out_limit = broom.Column(broom.Integer, broom.CheckConstraint("aces_out_limit >= 0"), server_default=broom.text("100"))
    managed_by_api = broom.Column(broom.Boolean, nullable=False, server_default=broom.text("FALSE"))

    # TODO: Make this a proper FK and add a relationship entry
    #       once the cross-dependency issues are sorted.
    acl_template_id = broom.Column(broom.Integer)

    vlan = broom.relationship("VLAN", back_populates="acl", uselist=False)
    aces = broom.relationship("ACEBase", back_populates="acl")

    ID = broom.stored('acl_id')
    VLANID = broom.stored('vlan_id')
    VLAN = broom.stored('vlan')
    DatacenterID = broom.stored('datacenter_id')
    ACEsOutLimit = broom.stored('aces_out_limit')
    ManagedByAPI = broom.stored('managed_by_api')
    _ACEs = broom.stored('aces')
    ACLTemplateID = broom.stored('acl_template_id')

    @broom.field
    def Datacenter(self):
        return self.DatacenterID()

    @broom.field
    def ACEs(self):
        return sorted(self._ACEs(), key=lambda v: v.OrderInACL())

    @broom.field
    def ACLTemplate(self):
        if self.ACLTemplateID():
            return self.db.read('ACLTemplate', self.ACLTemplateID())

    @broom.field
    def _CloudAPIACL(self):
        return self.db.find_one_by('CloudAPIACL',
                                   vlan_id       = self.VLANID(),
                                   datacenter_id = self.DatacenterID()
                                   )

    # TODO: Put on graph after implementing kwargs support.
    def _MatchesCloudAPI(self, includeTemplate=True):
        if includeTemplate:
            aclTemplate = self.ACLTemplate()
            if aclTemplate and not aclTemplate._MatchesCloudAPI():
                return False
        for ace in self.ACEs():
            if not ace._MatchesCloudAPI():
                return False
            return True
        return True

    @broom.field
    def _MismatchedACEs(self):
        return [ace for ace in self.ACEs() if not ace._MatchesCloudAPI()]

    # TODO: Put on graph after implementing kwargs support.
    def _CiscoFormat(self, includeTemplate=True):
        if includeTemplate and self.ACLTemplate():
            prefix = self.ACLTemplate().PrefixACL()._CiscoFormat()
            suffix = self.ACLTemplate().SuffixACL()._CiscoFormat()
        else:
            prefix = suffix = None
        aces = [ace._CiscoFormat() for ace in self.ACEs()]
        return "{prefix}{aces}{suffix}".format(
                prefix = (prefix + "\n") if prefix else '',
                suffix = suffix if suffix else '',
                aces = "\n".join(aces)
                )

    def ExtraToDictFields(self):
        return ['_CiscoFormat', '_MatchesCloudAPI', '_MismatchedACEs']
