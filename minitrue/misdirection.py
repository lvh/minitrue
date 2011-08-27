"""
Mechanism for misdirecting requests to different URLs easily.
"""
import urlparse

from twisted.python import log


def misdirector(f):
    """
    A decorator to turn something that modifies the URL a request is directed
    at into a request mangler.
    """
    def requestMangler(request):
        """
        A request mangler that misdirects a request to a different URL.
        """
        original = request.uri
        misdirected = f(original)

        if misdirected is None or misdirected == original:
            return

        log.msg("Misdirecting %s to %s..." % (original, misdirected))
        request.uri = misdirected

    return requestMangler


def affectHostnames(hostnames):
    def accessor(url):
        hostname = urlparse.urlsplit(url).hostname
        if hostname is not None:
            return hostname.lower()

    return _affect(hostnames, accessor=accessor, affectedMap=str.lower)


def affectPaths(paths):
    def accessor(url):
        return urlparse.urlsplit(url).path

    return _affect(paths, accessor=accessor)


def _affect(affected, accessor=None, affectedMap=None):
    if affectedMap is not None:
        affected = map(affectedMap, affected)

    def decorator(md):
        def decorated(url):
            this = url if accessor is None else accessor(url)

            if this in affected:
                return md(url)

        return decorated

    return decorator
