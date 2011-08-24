"""
Mechanism for misdirecting requests to different URLs easily.
"""
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