import broom

class Service(broom.BroomObject):
    __tablename__ = 'service'
    __table_args__ = (
            broom.UniqueConstraint("name"),
            )

    service_id = broom.Serial(__tablename__, primary_key=True)
    name = broom.Column(broom.String, nullable=False)
    description = broom.Column(broom.String)

    service_instantiations = broom.relationship("ServiceInstantiation", back_populates="service")

    ID = broom.stored('service_id')
    Name = broom.stored('name')
    Description = broom.stored('description')
    ServiceInstantiations = broom.stored('service_instantiations')

    @broom.field
    def ServiceInstantiationNames(self):
        return [si.Name() for si in self.ServiceInstantiations()]
