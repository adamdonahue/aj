import broom

class ACLTemplate(broom.BroomObject):

    __tablename__ = 'acl_template'

    acl_template_id = broom.Column(broom.Integer, primary_key=True, autoincrement=False)
    description = broom.Column(broom.String, nullable=False)
    prefix_acl_id = broom.Column(broom.Integer, broom.ForeignKey("acl.acl_id"), nullable=False)
    suffix_acl_id = broom.Column(broom.Integer, broom.ForeignKey("acl.acl_id"), nullable=False)

    prefix_acl = broom.relationship("ACL", foreign_keys=[prefix_acl_id])
    suffix_acl = broom.relationship("ACL", foreign_keys=[suffix_acl_id])

    ID = broom.stored('acl_template_id')
    Description = broom.stored('description')
    PrefixACL = broom.stored('prefix_acl')
    SuffixACL = broom.stored('suffix_acl')

    @broom.field
    def _CloudAPIACLTemplate(self):
        # XXX - Temporarily linked by enforcing svcmodel ID is equal
        #       to the cloudapi ID for acl_template.
        return self.db.read('CloudAPIACLTemplate', self.ID())

    @broom.field
    def _MatchesCloudAPI(self):
        return self.PrefixACL()._MatchesCloudAPI() \
                and self.SuffixACL()._MatchesCloudAPI()
