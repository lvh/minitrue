==========
 minitrue
==========

minitrue is a proxy designed to lie.

It does this by mangling the requests sent by the client before forwarding
them to the remote server, and mangling the responses sent by the server
before relaying them back to the client.

Note that this is little more than a proof of concept. If you want to do this
to any amount of traffic, there are better alternatives, such as `icap`_ in
combination with a proxy server such as `Squid`_.

.. _`icap`: http://tools.ietf.org/html/rfc3507
.. _`Squid`: http://www.squid-cache.org/

WAR IS PEACE
============

Like so many other tools, there are evil use cases for this tool. What you use
it for is entirely up to you.

FREEDOM IS SLAVERY
==================

The code is available under the very permissive `ISC license`_.  Contribution
is welcomed through the `Github project page`_.

.. _`ISC license`: http://www.isc.org/software/license
.. _`Github project page`: https://github.com/lvh/minitrue

IGNORANCE IS STRENGTH
=====================

This project doesn't come with a lot of documentation yet. Maybe, one day,
some documentation will be written. If you want to use it right now, the test
suite is a good place to start.
