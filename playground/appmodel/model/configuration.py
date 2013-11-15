import nodes

class Configuration(nodes.GraphObject):

    @nodes.graphMethod(nodes.Settable)
    def Settings(self):
        return []


class ConfigurationFile(nodes.GraphObject):

    @nodes.graphMethod(nodes.Settable)
    def ContentType(self):
        return 'plain/text'

