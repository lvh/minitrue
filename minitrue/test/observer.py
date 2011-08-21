"""
Tools for tests that observe the log.
"""
from twisted.python import log


class Observer(object):
    def __init__(self, predicate):
        self.observed = False
        self.predicate = predicate


    def __call__(self, event):
        if self.predicate(event):
            self.observed = True



class SubstringObserver(Observer):
    def __init__(self, substring):
        def predicate(event):
            try:
                return substring in event["message"][0]
            except (KeyError, IndexError):
                return False

        super(SubstringObserver, self).__init__(predicate)



class ObserverMixin(object):
    def setUp(self):
        """
        Creates an empty set of observers.
        """
        self.observers = set()


    def tearDown(self):
        """
        Removes all observers.
        """
        for observer in self.observers:
            log.removeObserver(observer)


    def addObserver(self, observer):
        """
        Adds an observer.
        """
        self.observers.add(observer)
        log.addObserver(observer)


    def verifyObserved(self, result, observer, expected=True):
        """
        Checks that a given observer has been observed.

        Returns the ``result`` argument unmodified. This is intended to be
        used as a deferred callback.
        """
        if expected:
            self.assertTrue(observer.observed)
        else:
            self.assertFalse(observer.observed)

        return result