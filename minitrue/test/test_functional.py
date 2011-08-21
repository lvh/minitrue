"""
High level functional tests for minitrue.
"""
import urlparse

from twisted.internet import reactor
from twisted.trial.unittest import TestCase
from twisted.web import server, resource

from minitrue import proxy
from minitrue.test.observer import ObserverMixin, SubstringObserver
from minitrue.test.connect import getWithProxy, getWithoutProxy
from minitrue.test.utils import Constructor


class _News(resource.Resource):
    """
    A news source in Oceania.
    """
    message = "Chocolate rations have been decreased to 20g per week."

    def render_GET(self, request):
        accept = request.getHeader("Accept-Language")
        if accept is not None and "oldspeak" in accept:
            language = "oldspeak"
        else:
            language = "newspeak"

        request.setHeader('Content-Language', language)
        return self.message



class _Book(resource.Resource):
    def render_GET(self, _):
        return "Chapter I: Ignorance is Strength\n\n..."



def buildTarget():
    root = resource.Resource()
    root.putChild("news", _News())
    root.putChild("book", _Book())

    return server.Site(root)



class _MinitrueConstructor(Constructor):
    factory = proxy.MinitrueFactory



misdirectingProxyConstructor = _MinitrueConstructor()
requestManglingProxyConstructor = _MinitrueConstructor()
responseManglingProxyConstructor = _MinitrueConstructor()


@misdirectingProxyConstructor.kwarg
def misdirector(url):
    """
    Misdirects requests to The Book towards a reputable news source.
    """
    if url.path == "/book":
        return url._replace(path="/news")

    return


@requestManglingProxyConstructor.kwarg
def requestMangler(request):
    """
    Modifies requests for oldspeak into requests for newspeak.
    """
    headers = request.requestHeaders
    headers.setRawHeaders("Accept-Language", ["newspeak"])


@responseManglingProxyConstructor.kwarg
def responseMangler(url, content):
    """
    Modifies some response content, because the chocolate rations have
    ostensibly not been decreased.
    """
    if "news" in url.path:
        return content.replace("decreased", "increased")

    return content



class ProxyTestMixin(object):
    def setUp(self):
        self.listeningPorts = {}

        proxyFactory = self.proxyConstructor()
        port = reactor.listenTCP(0, proxyFactory)
        self.listeningPorts["proxy"] = port

        target = buildTarget()
        port = reactor.listenTCP(0, target)
        self.listeningPorts["target"] = port


    def get(self, path="/", query="", fragment="", headers=None, proxy=True):
        url = self._buildURL(path, query, fragment)

        if proxy:
            proxy = self.listeningPorts["proxy"].getHost()
            return getWithProxy(url, proxy.host, proxy.port, headers)
        else:
            return getWithoutProxy(url, headers)


    def _buildURL(self, path, query, fragment):
        target = self.listeningPorts["target"].getHost()
        netloc = "%s:%s" % (target.host, target.port)
        parts = "http", netloc, path, query, fragment
        return urlparse.urlunsplit(parts)


    def tearDown(self):
        for port in self.listeningPorts.values():
            port.stopListening()



class MisdirectionTest(ProxyTestMixin, ObserverMixin, TestCase):
    proxyConstructor = misdirectingProxyConstructor

    def setUp(self):
        ProxyTestMixin.setUp(self)
        ObserverMixin.setUp(self)

        self.misdirectionObserver = SubstringObserver("Misdirecting")
        self.addObserver(self.misdirectionObserver)


    def tearDown(self):
        ProxyTestMixin.tearDown(self)
        ObserverMixin.tearDown(self)


    def verifyMisdirected(self, content, expected):
        if expected:
            self.assertIn("Chocolate rations", content)
        else:
            self.assertIn("Ignorance is Strength", content)

        return content


    def _misdirectionTest(self, withProxy):
        d = self.get("/book", proxy=withProxy).deferred
        d.addCallback(self.verifyMisdirected, withProxy)
        observer = self.misdirectionObserver
        d.addCallback(self.verifyObserved, observer, withProxy)
        return d


    def test_notMisdirected(self):
        return self._misdirectionTest(False)


    def test_misdirected(self):
        """
        Checks that requests to the book are misdirected somewhere else.
        """
        return self._misdirectionTest(True)
         




class RequestManglingTest(ProxyTestMixin, TestCase):
    proxyConstructor = requestManglingProxyConstructor

    def getInOldspeak(self, path="/", query="", fragment="", proxy=True):
        headers = {"Accept-Language": "oldspeak"}
        return self.get(path, query, fragment, headers, proxy)


    def verifyRequestMangled(self, content, factory, expectMangled=True):
        language, = factory.responseHeaders["content-language"]
        if expectMangled:
            self.assertEqual(language, "newspeak")
        else:
            self.assertEqual(language, "oldspeak")

        return content


    def _requestManglingTest(self, withProxy):
        factory = self.getInOldspeak("/news", proxy=withProxy)
        d = factory.deferred
        d.addCallback(self.verifyRequestMangled, factory, withProxy)
        return d        


    def test_requestNotMangled(self):
        return self._requestManglingTest(False)


    def test_requestMangled(self):
        return self._requestManglingTest(True)



class ResponseManglingTest(ProxyTestMixin, TestCase):
    proxyConstructor = responseManglingProxyConstructor

    def verifyResponseMangled(self, content, expectMangled):
        mangled = "increased" in content and "decreased" not in content

        if expectMangled:
            self.assertTrue(mangled)
        else:
            self.assertFalse(mangled)

        return content


    def _responseManglingTest(self, withProxy):
        d = self.get("/news", proxy=withProxy).deferred
        d.addCallback(self.verifyResponseMangled, withProxy)
        return d


    def test_responseNotMangled(self):
        return self._responseManglingTest(False)


    def test_responseMangled(self):
        return self._responseManglingTest(True)
