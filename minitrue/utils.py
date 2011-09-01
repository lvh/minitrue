"""
Generically useful utilities.
"""
import urlparse

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



def passthrough(f):
    def callback(result, *a, **kw):
        f(*a, **kw)
        return result
    return callback


def replace(url, **kw):
    split = urlparse.urlsplit(url)._replace(**kw)
    return urlparse.urlunsplit(split)



class Combined(object):
    def __init__(self):
        self._fs = []


    def part(self, f):
        self._fs.append(f)
        return f


    def __call__(self, *a, **kw):
        for f in self._fs:
            f(*a, **kw)
