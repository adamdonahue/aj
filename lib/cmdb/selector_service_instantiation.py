import broom

class SelectorServiceInstantiation(broom.BroomObject):

    __tablename__ = 'selector_service_instantiation'
    __table_args__ = (
            broom.UniqueConstraint("selector_id", "service_instantiation_id", "service_instantiation_role"),
            )
    selector_service_instantiation_id = broom.Serial(__tablename__, primary_key=True)
    selector_id = broom.Column(broom.Integer, broom.ForeignKey('selector.selector_id'), nullable=False)
    service_instantiation_id = broom.Column(broom.Integer, broom.ForeignKey('service_instantiation.service_instantiation_id'), nullable=False)
    service_instantiation_role = broom.Column(broom.String, server_default=broom.text("'default'"), nullable=False)

    selector = broom.relationship("Selector", back_populates="selector_service_instantiations")
    service_instantiation = broom.relationship("ServiceInstantiation", back_populates="_selectors_by_role")

    Role = broom.stored('service_instantiation_role')
    Selector = broom.stored('selector')
    ServiceInstantiation = broom.stored('service_instantiation')

    @broom.field
    def Service(self):
        return self.ServiceInstantiation().Service()

