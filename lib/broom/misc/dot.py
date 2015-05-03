import broom
import broom.visitor
import subprocess
import tempfile
import webbrowser

class DotGrapher(broom.visitor.GraphDepthFirstVisitor):

    def __init__(self):
        self.nodes = {}
        self.edges = []

    def nodeName(self, node):
        return 'N%s' % hash(node)

    def visitNode(self, node):
        name = self.nodeName(node)
        if name not in self.nodes:
            self.nodes[name] = node
        if self._path:
            self.edges.append((self.nodeName(self._path[-1]), name))

    def asDot(self, node):
        """Returns string containing .dot representation
        of the subgraph rooted at node.

        """
        raise NotImplementedError()

    def asDotFile(self, node, fileName=None):
        """Generates dot content, writes it to the specified
        file, and returns that file's path.

        If no fileName is specified a random name is
        generated and used for the output.

        """
        dotData = self.asDot(node)
        fileName = fileName or tempfile.mktemp(suffix=".dot")
        with open(fileName, 'w') as f:
            f.write(dotData)
            f.flush()
        return f.name

    def asSvg(self, node):
        """Generates SVG of the provided node's subgraph
        and returns it as a string.

        """
        raise NotImplementedError()

    def nodeName(self, node):
        """Returns a unique name identifying the GraphViz
        node entry in the generate dot file.

        """
        return 'N%s' % hash(node)

    def nodeAttributes(self, node):
        """Returns a dictionary representing the GraphViz
        attributes to assign to the node.

        """
        return {'label': self.nodeLabel(node)}

    def nodeLabel(self, node):
        """Returns a label for the specified node.

        """
        raise NotImplementedError()

    def edgeAttributes(self, node, inputNode):
        """Returns a dictionary of attributes for the
        specified edge.  An edge is a node and
        one of its inputs.

        """
        label = self.edgeLabel(node, inputNode)
        if label is None:
            return {}
        return {'label': label}

    def edgeLabel(self, node, inputNode):
        """Returns a label for the specified edge.

        By default no label is returned.

        """
        return None


