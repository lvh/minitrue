==========
 minitrue
==========

minitrue is an HTTP proxy server designed to lie.

There are three main tools in its arsenal of deception: misdirection,
request mangling and response mangling.

Misdirection means the proxy server sends the request to a different
URL. Simple examples of that could be some kind of captive portal, a
notice that page has been blocked...

Response mangling means the proxy server modifies the response before
forwarding it back to the client. People have used similar tricks to
pranks pranks_ on people stealing their wireless connection.

.. _pranks: http://www.ex-parrot.com/pete/upside-down-ternet.html

Request mangling is like response mangling, but it changes the request
sent to the remote HTTP server instead of mangling that server's
response before it's forwarded to the client.

All of these tools can be used at once.

Note that this is little more than a proof of concept. If you want to
do this to any amount of traffic, there are better alternatives, such
as `icap`_ in combination with a proxy server such as `Squid`_.

.. _`icap`: http://tools.ietf.org/html/rfc3507
.. _`Squid`: http://www.squid-cache.org/

WAR IS PEACE
============

Obviously, this is not a very nice thing to do to people behind their
backs. Fortunately, there are also more benign purposes. What you use
this tool for is up to you.

FREEDOM IS SLAVERY
==================

The code is available under the very permissive `ISC license`_.
Contribution is welcomed through the `Github project page`_.

.. _`ISC license`: http://www.isc.org/software/license
.. _`Github project page`: https://github.com/lvh/minitrue

IGNORANCE IS STRENGTH
=====================

This project doesn't come with a lot of documentation yet. Maybe one
day I will write some.
