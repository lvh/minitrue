"""
Generically useful utilities.
"""
try: # pragma: no cover
    from cStringIO import StringIO; StringIO
except ImportError:
    from StringIO import StringIO; StringIO


class Constructor(object):
    def __init__(self):
        self.kw = {}


    def kwarg(self, f):
        """
        Decorator to pass a function as a kwarg on construction.
        """
        self.kw[f.__name__] = f
        return f


    def __call__(self):
        return self.factory(**self.kw)