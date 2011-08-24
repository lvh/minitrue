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


    def kwarg(self, kwargName=None):
        """
        Decorator to pass a function as a kwarg on construction.
        """
        def decorator(f):
            name = f.__name__ if kwargName is None else kwargName
            self.kw[name] = f
            return f
        return decorator


    def __call__(self):
        return self.factory(**self.kw)