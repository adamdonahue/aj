import broom

class ServiceEndpoint(broom.BroomObject):
    """A service instantiation endpoint."""

    __tablename__ = 'service_endpoint'

    service_endpoint_id = broom.Serial(__tablename__, primary_key=True)
