import nodes

class ServiceCollection(nodes.GraphObject):
    """A collection of services.

    NOTES
    -----

    37signals, for example, provides status via its status page
    (http://status.37signals.com/) for these high-level applications:
    Basecamp, Highrise, Campfire, and so forth.  GitHub provides general
    availability status for GitHub.com, Storage, GitHub Pages, API
    and Code Downloads.

    


    """
    @nodes.graphMethod(nodes.Settable)
    def ServiceObjects(self):
        return []

class Service(nodes.GraphObject):
    pass

class ServiceEndPoint(nodes.GraphObject):

    @nodes.graphMethod(nodes.Settable)
    def IPAddress(self):
        return None

    @nodes.graphMethod(nodes.Settable)
    def PortNumber(self):
        return None

    @nodes.graphMethod(nodes.Settable)
    def Protocol(self):
        return None

