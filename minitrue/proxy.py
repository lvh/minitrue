"""
HTTP proxy facilities.
"""
import functools
import urlparse
try: # pragma: no cover
    import cStringIO as StringIO; StringIO
except ImportError:
    import StringIO

from twisted.python import log
from twisted.web import http, proxy


class _Response(object):
    code = None

    def __init__(self, client):
        self.client = client
        self.content = StringIO.StringIO()



def onlyWhenMangling(f):
    @functools.wraps(f)
    def decorated(self, *a, **kw):
        if self.mangler is None:
            m = getattr(proxy.ProxyClient, f.__name__)
        else:
            m = f

        return m(self, *a, **kw)
    return decorated



class MinitrueClient(proxy.ProxyClient):
    """
    Client that makes a request on behalf of this proxy server.
    """
    def __init__(self, father, command, rest, headers, content, mangler=None):
        self.father = father
        self.command = command
        self.rest = rest
        self._setScrubbedHeaders(headers)
        self.content = content
        self.mangler = mangler
        if mangler is not None:
            self.response = _Response(self)


    def _setScrubbedHeaders(self, headers):
        if "proxy-connection" in headers:
            del headers["proxy-connection"]
        headers["connection"] = "close"

        self.headers = headers


    def connectionMade(self):
        """
        Called when a connection is made.

        This forwards the request data to the remote server.
        """
        self.sendCommand(self.command, self.rest)
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


    @onlyWhenMangling
    def handleStatus(self, version, code, message):
        self.response.code = int(code)
        proxy.ProxyClient.handleStatus(self, version, code, message)


    @onlyWhenMangling
    def handleEndHeaders(self):
        """
        Makes the response headers available on the response object.
        """
        self.response.headers = self.father.responseHeaders


    @onlyWhenMangling
    def handleResponsePart(self, part):
        """
        Saves a part of the response body.
        """
        self.response.content.write(part)


    @onlyWhenMangling
    def handleResponseEnd(self):
        """
        Mangles the received response, and then replays that response to
        the client using the proxy.

        Closes both the connection to the client and the server.
        """
        if self._finished:
            return
        self._finished = True
            
        self.transport.loseConnection()
        self.mangler(self.response)
        self._replayContent()
        self.father.transport.loseConnection()


    def _replayContent(self):
        """
        Replays the (potentially mangled) content of the response object.
        """
        content = self.response.content
        content.seek(0, 0)
        self.father.write(content.read())
        self.father.finish()



class MinitrueClientFactory(proxy.ProxyClientFactory):
    """
    Factory that builds clients to make requests on behalf of a proxy server.
    """
    protocol = MinitrueClient
    noisy = False

    def __init__(self, father, method, path, headers, content, mangler=None):
        self.protocolArgs = father, method, path, headers, content, mangler


    def buildProtocol(self, _):
        return self.protocol(*self.protocolArgs)



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
        self.responseMangler = responseMangler


    def process(self):
        """
        Processes this request.
        """
        self.mangle()

        url = self._getURL()

        host, port = self._getHostAndPort(url.netloc, url.scheme)
        path = _getRestOfURL(url)
        headers = self._buildHeaders(host)
        
        builder = self._getClientFactoryBuilder(url.scheme)
        clientFactory = builder(path=path, headers=headers)
        self.reactor.connectTCP(host, port, clientFactory)


    def mangle(self):
        """
        No-op request mangler.
        """


    def _getClientFactoryBuilder(self, scheme):
        cls = self.protocols[scheme]
        mangler = self.responseMangler
        builder = functools.partial(cls, father=self, method=self.method,
                                    content=self.content, mangler=mangler)
        return builder


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
        if self.misdirector is None:
            return original
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
        if self.requestMangler is not None:
            def mangle():
                self.requestMangler(request)
            request.mangle = mangle

        return request



class MinitrueFactory(http.HTTPFactory):
    """
    A factory that builds proxies.
    """
    protocol = Minitrue
    noisy = False

    def __init__(self, misdirector=None, requestMangler=None, responseMangler=None):
        http.HTTPFactory.__init__(self)
        self.misdirector = misdirector
        self.requestMangler = requestMangler
        self.responseMangler = responseMangler


    def buildProtocol(self, _):
        """
        Creates a new proxy protocol instance to talk to the client.
        """
        return self.protocol(requestMangler=self.requestMangler,
                             responseMangler=self.responseMangler,
                             misdirector=self.misdirector)
