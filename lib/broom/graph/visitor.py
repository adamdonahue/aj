import broom

class GraphVisitor(object):
    """A graph visitor.  Default traversal is breadth-
    first, but subclasses may use different strategies.

    """
    def visit(self, node, args=()):
        """Visit the graph starting at the given node, or
        graph field and arguments, which are resolved to
        a node.

        """
        if not isinstance(node, broom.Node):
            node = node.node(*args)
        self.visitGraph(node)

    def visitGraph(self, node):
        """Performs a breadth-first search of the graph
        beginning at the specified node.

        """
        nodes = [node]
        while nodes:
            currentNode = nodes.pop()
            self.visitNode(currentNode)
            if currentNode.fixed() or not currentNode.valid():
                continue
            nodes.append(currentNode.inputs)

class GraphDepthFirstVisitor(GraphVisitor):
    """A depth-first graph visitor"""

    def _visitGraph(self, node):
        if not node.fixed():
            self._path.append(node)
            for inputNode in node.inputs:
                self._visitGraph(inputNode)
            self._path.pop()
        self.visitNode(node)

    def visitGraph(self, node):
        """Visits graph nodes depth first, keeping
        track of the current ancestry for each node.

        """
        self._path = []
        self._visitGraph(node)
