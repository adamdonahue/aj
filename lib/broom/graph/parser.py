import ast

class BroomRef(object):
    """A reference to an AST node parsed by the BroomParser.

    (Don't confuse AST nodes with graph nodes; they are different.

    """
    def __init__(self, node):
        self.node = node

    def __hash__(self):
        return hash(self.id.name)

class BroomNameRef(BroomRef):

    def __init__(self, node):
        self.node = node

    def __hash__(self):
        return hash(self.node.id)

class BroomArgRef(BroomRef):

    def __init__(self, node):
        self.node = node

class BroomSelfRef(BroomRef):

    def __init__(self, node):
        self.node = node

class BroomGraphMethodRef(BroomRef):

    def __init__(self, node):
        self.node = node

class BroomParser(ast.NodeTransformer):
    """Transform a decorated BroomObject into a version
    that is aware of its dependencies without first
    having to execute a call path through those
    dependendencies.

    """
    # NOTES:
    #
    # The general strategy we'll try first here is
    # to transform any node calls (and references?)
    # into arguments of a graph method.
    #
    # For example, if I have the graph method:
    #
    # def X(self):
    #    q = 20
    #    return q * self.Y() * self.Z()
    #
    # then this will be rewritten into:
    #
    # def X(self, __INPUTS__):
    #    q = 20
    #    return q * __INPUTS__[0] * __INPUTS__[1]
    #
    # (We'll need to track which index maps to a given node.)
    #
    # def X(self, x):
    #    return x * self.Y() * self.Z()
    #
    # becomes
    #
    # def X(self, __INPUTS__):
    #    return __INPUTS__[0] * __INPUTS__[1] * __INPUTS__[2]
    #
    # [That is, arguments to graph methods are themselves on the
    # graph.]
    #
    # def X(self):
    #     return self.Y().Z()
    #
    # becomes
    #
    # def X(self, __INPUTS__):
    #     return __INPUTS__[0].Z()
    #
    # or does it?  I think it should.
    #
    # Can we track things that are copied off?  Let's see:
    #
    # def X(self):
    #    y = self.Y()
    #    z = y.Z()
    #    return z
    #
    # If we do this naively:
    #
    # def X(self, __INPUTS__):
    #    y = __INPUTS__[0]
    #    z = y.Z()
    #    return z
    #
    # then will this work?  No, because we've now lost detail
    # on the fact that X depends on Z.  I can get the right
    # results when computing the node, but if I haven't done
    # that then I don't know, from this parser, that X depends
    # on Y's Z.  I know it depends on Y, but not on Y's Z.
    #
    # How might we handle this? One way is to track assignments
    # from graph field calls.
    #
    # For example, if I assign to y from a graph node then
    # I can note that it's a graph method.  If y is then changed
    # to a non-graph method, then I can remove that notation.
    # If Z is called via y, then I know whether it was called
    # as a graph method or not.
    #
    # TODO
    # ----
    # Have to handle some other variables:
    #     self
    #     self.db       <-- This is on-graph.
    #     broom.db        <-- This is on-graph but should we
    #                       require self.db notation in object calls?
    #
    # If/then statements.  Do we defer these?
    #
    # List and list comprehensions.
    #
    #    The format [x for x in self.Y()]
    #
    # if tricky, because I won't know what x is until evaluation
    # time.
    #
    # What about?
    #
    #   [x.Z() for x in self.Y()]
    #
    # Is this any better.  Well, theoretically, no, because
    # self.Y() can return a bunch of other items.  I suppose
    # this is the same as x if we track it.  We just have to
    # know that the variable is a graph object and anything
    # called from it is a graph method.
    #
    # The question is how tricky this becomes...
    #
    def __init__(self):
        self._inputs = []
        self._refs = set()

    def parse(self, *args):
        raise NotImplementedError()

    def parse_s(self, s):
        """Test parser for arbitrary Python code strings."""
        raise NotImplementedError()

    def generic_visit(self, node):
        return super(self.__class__, self).generic_visit(node)

    def visit_Name(self, node):
        node.ref = BroomNameRef(node)
        self._refs.add(node.ref)
        return node

    def visit_FunctionDef(self, node):
        for arg in node.args.args[1:]:
            self._inputs.append(arg.id)
        self._argc = len(node.args.args[1:])
        node.args.args[1:] = []
        for i,b in enumerate(node.body):
            node.body[i] = self.visit(b)
        if self._inputs:
            node.args.args.append(ast.Name('__INPUTS__', ast.Param()))
        return node

    def visit_Call(self, node):
        node.func = self.visit(node.func)
        if isinstance(node.func, ast.Name) and node.func.id in self._inputs:
            return ast.Name('__INPUTS__', ast.Load())
        return self.generic_visit(node)

    def visit_Return(self, node):
        node.value = self.visit(node.value)
        return node


s = """
def X(self, x):
    z = x + self.Y() + self.Y()
    return self.Z() + z
"""

t = """
def X(self, __INPUTS__):
    return __INPUTS__[0]
"""

node = ast.parse(s)
visitor = BroomParser()
visitor.visit(node)

for r in visitor._refs:
    print r.node.id
print visitor._refs

import codegen
print codegen.to_source(node)
