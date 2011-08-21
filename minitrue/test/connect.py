"""
Connects to web sites, with and without proxies.
"""
import urlparse

from twisted.internet import reactor
from twisted.web import client


def _gotHeaders(self, headers):
    client.HTTPClientFactory.gotHeaders(self, headers)
    self.responseHeaders = headers



class _ProxyClientFactory(client.HTTPClientFactory):
    """
    A client factory that uses a proxy.
    """
    gotHeaders = _gotHeaders

    def setURL(self, url):
        client.HTTPClientFactory.setURL(self, url)
        self.path = url



def getWithProxy(url, proxyHost, proxyPort, headers=None):
    factory = _ProxyClientFactory(url, headers=headers)
    reactor.connectTCP(proxyHost, proxyPort, factory)
    return factory



class _HTTPClientFactory(client.HTTPClientFactory):
    """
    A client factory that does not use a proxy.
    """
    gotHeaders = _gotHeaders


def getWithoutProxy(url, headers=None):
    factory = _HTTPClientFactory(url, headers=headers)
    splitURL = urlparse.urlsplit(url)
    host, port = splitURL.hostname, splitURL.port or 80
    reactor.connectTCP(host, port, factory)
    return factory