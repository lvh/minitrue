"""
HTTP proxy facilities.
"""
from twisted.python import log
from twisted.web import http, proxy

import urlparse


class MinitrueClient(proxy.ProxyClient):
    """
    Client that makes a request on behalf of this proxy server.
    """
    def __init__(self, father, command, rest, headers, content):
        self.father = father

        def _sendCommand():
            self.sendCommand(command, rest)
        self._sendCommand = _sendCommand

        if "proxy-connection" in headers:
            del headers["proxy-connection"]
        headers["connection"] = "close"
 
        self.headers = headers
        self.content = content


    def connectionMade(self):
        """
        Called when a connection is made.

        This forwards the request data to the remote server.
        """
        self._sendCommand()
        self._sendHeaders()
        self._sendRequestBody()


    def _sendHeaders(self):
        """
        Sends the headers to the server.
        """
        for header, value in self.headers.items():
            self.sendHeader(header, value)
        
        self.endHeaders()


    def _sendRequestBody(self):
        """
        Sends the request body to the server.
        """
        self.content.seek(0, 0)
        data = self.content.read()
        self.transport.write(data)



class MinitrueClientFactory(proxy.ProxyClientFactory):
    """
    Factory that builds clients to make requests on behalf of a proxy server.
    """
    protocol = MinitrueClient
    noisy = False

    def __init__(self, father, command, rest, headers, content):
        self.father = father

        self.command = command
        self.rest = rest
        self.headers = headers
        self.content = content


    def buildProtocol(self, _):
        httpArgs = self.command, self.rest, self.headers, self.content
        return self.protocol(self.father, *httpArgs)



def _getRestOfURL(splitURL):
    """
    Gets the rest of the URL, after stripping the netloc and scheme.

    This is basically the path, query and fragment. If that would have
    been empty, ``/`` is returned instead.
    """
    parts = ("", "") + splitURL[2:]
    return urlparse.urlunsplit(parts) or "/"



class MinitrueRequest(proxy.ProxyRequest):
    """
    A request made to a proxy server that forwards that request to a remote
    server on behalf of the client.
    """
    protocols = {'http': MinitrueClientFactory}

    def __init__(self, channel, queued, misdirector, responseMangler):
        proxy.ProxyRequest.__init__(self, channel, queued)
        self.misdirector = misdirector


    def process(self):
        """
        Processes this request.
        """
        self.mangle()

        url = self._getURL()

        host, port = self._getHostAndPort(url.netloc, url.scheme)
        rest = _getRestOfURL(url)
        headers = self._buildHeaders(host)

        cls = self.protocols[url.scheme]
        clientFactory = cls(self, self.method, rest, headers, self.content)
        self.reactor.connectTCP(host, port, clientFactory)


    def _getHostAndPort(self, netloc, scheme):
        """
        Gets the appropriate host and port to connect to.

        The host and port are derived from the netloc. If the netloc does not
        specify the port, the default port for the specified scheme is used.
        """
        host, port = netloc, self.ports[scheme]
        if ":" in host:
            host, port = host.split(":")
            port = int(port)

        return host, port


    def _getURL(self):
        """
        Gets the target URL for this request.

        This applies the misdirect function to the split URL. If the URL has
        changed, this change is logged.
        """
        original = urlparse.urlsplit(self.uri)
        misdirected = self.misdirector(original)

        if misdirected is None:
            return original
        elif misdirected != original:
            src, dest = map(urlparse.urlunsplit, [original, misdirected])
            log.msg("Misdirecting %s to %s" % (src, dest))

        return misdirected



    def _buildHeaders(self, host):
        """
        Builds the headers for the outgoing request.

        This copies the incoming headers and sets the ``Host`` header if it
        hasn't been set.
        """
        headers = self.getAllHeaders().copy()
        if 'host' not in headers:
            headers["host"] = host

        return headers



class Minitrue(proxy.Proxy):
    """
    A proxy.
    """
    requestFactoryClass = MinitrueRequest

    def __init__(self, **kwargs):
        proxy.Proxy.__init__(self)
        self.requestMangler = kwargs.pop("requestMangler")
        self.kwargs = kwargs


    def requestFactory(self, *args, **kwargs):
        """
        Builds a new request by calling C{self.requestClass}.
        """
        kwargs.update(self.kwargs)
        request = self.requestFactoryClass(*args, **kwargs)
        request.mangle = lambda: self.requestMangler(request)
        return request



def identity(a):
    """
    The identity function (sort of).

    Returns whatever it is passed unmodified, regardless of what the
    arguments were.

    This is a no-op request mangler, response mangler and misdirector.
    """
    return a



class MinitrueFactory(http.HTTPFactory):
    """
    A factory that builds proxies.
    """
    protocol = Minitrue
    noisy = False

    def __init__(self, **kwargs):
        http.HTTPFactory.__init__(self)
        for key in ("misdirector", "requestMangler", "responseMangler"):
            if key not in kwargs:
                kwargs[key] = identity
        self.kwargs = kwargs


    def buildProtocol(self, _):
        """
        Creates a new proxy protocol instance to talk to the client.
        """
        return self.protocol(**self.kwargs)
