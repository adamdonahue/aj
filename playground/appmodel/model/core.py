import nodes

class Resource(nodes.GraphObject):

    @nodes.graphMethod(nodes.Settable)
    def Name(self):
        return None

    @nodes.graphMethod(nodes.Settable)
    def Relationships(self):
        return []

class Edge(nodes.GraphObject):

    @nodes.graphMethod
    def SourceLabel(self):
        return 'uses'

    @nodes.graphMethod
    def TargetLabel(self):
        return 'used by'

    @nodes.graphMethod(nodes.Settable)
    def SourceResource(self):
        return None

    @nodes.graphMethod(nodes.Settable)
    def TargetResource(self):
        return None
