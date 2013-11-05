import broom

class ServiceInstantiation(broom.BroomObject):

    __tablename__ = 'service_instantiation'
    __table_args__ = (
            broom.UniqueConstraint("name"),
            broom.UniqueConstraint("domain_name", "port", "transport_protocol")
            )

    service_instantiation_id = broom.Serial(__tablename__, primary_key=True)
    service_id = broom.Column('service_id', broom.Integer, broom.ForeignKey('service.service_id'), nullable=False)
    name = broom.Column('name', broom.String, nullable=False)
    domain_name = broom.Column('domain_name', broom.String, nullable=False)
    port = broom.Column('port', broom.Integer)
    transport_protocol = broom.Column('transport_protocol', broom.String, nullable=False)
    application_protocol = broom.Column('application_protocol', broom.String)

    service = broom.relationship("Service", back_populates="service_instantiations")
    _selectors_by_role = broom.relationship("SelectorServiceInstantiation", back_populates="service_instantiation")

    ID = broom.stored('service_instantiation_id')
    Service = broom.stored('service')
    Name = broom.stored('name')
    DomainName = broom.stored('domain_name')
    Port = broom.stored('port')
    TransportProtocol = broom.stored('transport_protocol')
    ApplicationProtocol = broom.stored('application_protocol')
    _SelectorsByRole = broom.stored('_selectors_by_role')

    @broom.field
    def SelectorsByRole(self):
        return dict((a.Role(), a.Selector()) for a in self._SelectorsByRole())
