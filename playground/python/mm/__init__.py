"""Sample library for multiple dispatch."""

import types

def Multimethod(object):

    MULTIMETHODS = {}

    def __new__(self, klass, bases, attrs):
        print self, klass, bases, attrs
        return super(Multimethod, self).__new__(klass, bases, attrs)

    # Needs module.
    def __init__(self, name):
        self.name = name

def multimethod(f=None, *types_, **kwargs):
    if kwargs:
        raise RuntimeError("multimethods do not support keywords args")

    # Two call types:
    #
    #   @multimethod
    #   def f(...): ...
    #
    # Disallow for now, but could make sense in future as a
    # default.

    if type(f) != types.FunctionType:
        def w(f, *args):
            return multimethod(f, *args)
        return w


m = Multimethod('foo')
