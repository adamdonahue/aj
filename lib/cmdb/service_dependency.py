import broom

class ServiceDependency(broom.BroomObject):

    @broom.field(broom.Settable)
    def ServiceEndpoint(self):
        return None

    def setServiceEndpoint(self, value):
        return [broom.NodeChange(self.ServiceEndpoint, value)]

    @broom.field(delegate=setServiceEndpoint)
    def InstanceName(self):
        return self.ServiceEndpoint()

    @broom.field(broom.Settable)
    def ServiceInstantiations(self):
        return []

    @broom.field(broom.Settable)
    def ServiceInstantiationRole(self):
        return None
