#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2008-2010, Bryan Davis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright 
#     notice, this list of conditions and the following disclaimer in the 
#     documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
"""Utitlities for dealing with ip addresses.

  Functions:
    - validate_ip: Validate a dotted-quad ip address.
    - ip2long: Convert a dotted-quad ip address to a network byte order 32-bit 
      integer.
    - long2ip: Convert a network byte order 32-bit integer to a dotted quad ip 
      address.
    - ip2hex: Convert a dotted-quad ip address to a hex encoded network byte
      order 32-bit integer.
    - hex2ip: Convert a hex encoded network byte order 32-bit integer to a
      dotted-quad ip address.
    - validate_cidr: Validate a CIDR notation ip address.
    - cidr2block: Convert a CIDR notation ip address into a tuple containing 
      network block start and end addresses.

  Objects:
    - IpRange: Range of ip addresses providing ``in`` and iteration.
    - IpRangeList: List of IpRange objects providing ``in`` and iteration.


  The IpRangeList object can be used in a django settings file to allow CIDR 
  notation and/or (start, end) ranges to be used in the INTERNAL_IPS list.

  Example:
    INTERNAL_IPS = IpRangeList(
        '127.0.0.1',
        '192.168/16',
        ('10.0.0.1', '10.0.0.19'),
        )

"""
__version__ = '0.1'

__all__ = (
        'validate_ip', 'ip2long', 'long2ip', 'ip2hex', 'hex2ip',
        'validate_cidr', 'cidr2block',
        'IpRange', 'IpRangeList',
        )

import re

_DOTTED_QUAD_RE = re.compile(r'^(\d{1,3}\.){0,3}\d{1,3}$')

def validate_ip (str):
    """Validate a dotted-quad ip address.

    The string is considered a valid dotted-quad address if it consists of 
    one to four octets (0-255) seperated by periods (.).


    >>> validate_ip('127.0.0.1')
    True

    >>> validate_ip('127.0')
    True

    >>> validate_ip('127.0.0.256')
    False

    >>> validate_ip(None)
    Traceback (most recent call last):
        ...
    TypeError: expected string or buffer


    Args:
        str: String to validate as a dotted-quad ip address
    Returns:
        True if str is a valid dotted-quad ip address, False otherwise
    """
    if _DOTTED_QUAD_RE.match(str):
        quads = str.split('.')
        for q in quads:
            if int(q) > 255:
                return False
        return True
    return False
#end validate_ip

_CIDR_RE = re.compile(r'^(\d{1,3}\.){0,3}\d{1,3}/\d{1,2}$')

def validate_cidr (str):
    """Validate a CIDR notation ip address.

    The string is considered a valid CIDR address if it consists of one to 
    four octets (0-255) seperated by periods (.) followed by a forward slash 
    (/) and a bit mask length (1-32).


    >>> validate_cidr('127.0.0.1/32')
    True

    >>> validate_cidr('127.0/8')
    True

    >>> validate_cidr('127.0.0.256/32')
    False

    >>> validate_cidr('127.0.0.0')
    False

    >>> validate_cidr(None)
    Traceback (most recent call last):
        ...
    TypeError: expected string or buffer


    Args:
        str: String to validate as a CIDR ip address
    Returns:
        True if str is a valid CIDR address, False otherwise
    """
    if _CIDR_RE.match(str):
        ip, mask = str.split('/')
        if validate_ip(ip):
            if int(mask) > 32:
                return False
        else:
            return False
        return True
    return False
#end validate_cidr

def ip2long (ip):
    """
    Convert a dotted-quad ip address to a network byte order 32-bit integer.


    >>> ip2long('127.0.0.1')
    2130706433L

    >>> ip2long('127.1')
    2130706433L

    >>> ip2long('127')
    2130706432L

    >>> ip2long('127.0.0.256') is None
    True


    Args:
        ip: Dotted-quad ip address (eg. '127.0.0.1')

    Returns:
        Network byte order 32-bit integer or None if ip is invalid
    """
    if not validate_ip(ip):
        return None
    quads = ip.split('.')
    if len(quads) == 1:
        # only a network quad
        quads = quads + [0, 0, 0]
    elif len(quads) < 4:
        # partial form, last supplied quad is host address, rest is network
        host = quads[-1:]
        quads = quads[:-1] + [0,] * (4 - len(quads)) + host

    lngip = 0
    for q in quads:
        lngip = (lngip << 8L) | int(q)
    return lngip
#end ip2long

_MAX_IP = 0xffffffffL

def long2ip (l):
    """
    Convert a network byte order 32-bit integer to a dotted quad ip address.


    >>> long2ip(2130706433)
    '127.0.0.1'

    >>> long2ip(None)
    Traceback (most recent call last):
        ...
    TypeError: unsupported operand type(s) for >>: 'NoneType' and 'int'


    Args:
        l: Network byte order 32-bit integer
    Returns:
        Dotted-quad ip address (eg. '127.0.0.1')
    """
    if _MAX_IP < l < 0:
        raise TypeError, "expected int between 0 and %d inclusive" % _MAX_IP
    return '%d.%d.%d.%d' % (l>>24 & 255, l>>16 & 255, l>>8 & 255, l & 255) 
#end long2ip

def ip2hex (addr):
    """
    Convert a dotted-quad ip address to a hex encoded number.

    >>> ip2hex('0.0.0.1')
    '00000001'
    >>> ip2hex('127.0.0.1')
    '7f000001'
    >>> ip2hex('127.255.255.255')
    '7fffffff'
    >>> ip2hex('128.0.0.1')
    '80000001'
    >>> ip2hex('128.1')
    '80000001'
    >>> ip2hex('255.255.255.255')
    'ffffffff'

    """
    netip = ip2long(addr)
    if netip is None:
        return None
    return "%08x" % netip
#end ip2hex

def hex2ip (hex_str):
    """
    Convert a hex encoded integer to a dotted-quad ip address.

    >>> hex2ip('00000001')
    '0.0.0.1'
    >>> hex2ip('7f000001')
    '127.0.0.1'
    >>> hex2ip('7fffffff')
    '127.255.255.255'
    >>> hex2ip('80000001')
    '128.0.0.1'
    >>> hex2ip('ffffffff')
    '255.255.255.255'

    """
    try:
        netip = int(hex_str, 16)
    except ValueError:
        return None
    return long2ip(netip)
#end hex2ip

def cidr2block (cidr):
    """
    Convert a CIDR notation ip address into a tuple containing the network 
    block start and end addresses.


    >>> cidr2block('127.0.0.1/32')
    ('127.0.0.1', '127.0.0.1')

    >>> cidr2block('127/8')
    ('127.0.0.0', '127.255.255.255')

    >>> cidr2block('127.0.1/16')
    ('127.0.0.0', '127.0.255.255')

    >>> cidr2block('127.1/24')
    ('127.1.0.0', '127.1.0.255')

    >>> cidr2block('127.0.0.3/29')
    ('127.0.0.0', '127.0.0.7')

    >>> cidr2block('127/0')
    ('0.0.0.0', '255.255.255.255')


    Args:
        cidr: CIDR notation ip address (eg. '127.0.0.1/8')
    Returns:
        Tuple of block (start, end) or None if invalid
    """
    if not validate_cidr(cidr):
        return None

    ip, prefix = cidr.split('/')
    prefix = int(prefix)

    # convert dotted-quad ip to base network number
    # can't use ip2long because partial addresses are treated as all network 
    # instead of network plus host (eg. '127.1' expands to '127.1.0.0')
    quads = ip.split('.')
    baseIp = 0
    for i in range(4):
        baseIp = (baseIp << 8L) | int(len(quads) > i and quads[i] or 0)

    # keep left most prefix bits of baseIp
    shift = 32 - prefix
    start = baseIp >> shift << shift

    # expand right most 32 - prefix bits to 1
    mask = (1 << shift) - 1
    end = start | mask
    return (long2ip(start), long2ip(end))
#end cidr2block

class IpRange (object):
    """
    Range of ip addresses.

    Converts a CIDR notation address, tuple of ip addresses or start and end 
    addresses into a smart object which can perform ``in`` and ``not in`` 
    tests and iterate all of the addresses in the range.


    >>> r = IpRange('127.0.0.1', '127.255.255.255')
    >>> '127.127.127.127' in r
    True

    >>> '10.0.0.1' in r
    False

    >>> 2130706433 in r
    True

    >>> r = IpRange('127/24')
    >>> print r
    ('127.0.0.0', '127.0.0.255')

    >>> r = IpRange('127/30')
    >>> for ip in r:
    ...     print ip
    127.0.0.0
    127.0.0.1
    127.0.0.2
    127.0.0.3

    >>> print IpRange('127.0.0.255', '127.0.0.0')
    ('127.0.0.0', '127.0.0.255')
    """
    def __init__ (self, start, end=None):
        """
        Args:
            start: Ip address in dotted quad format or CIDR notation or tuple 
                of ip addresses in dotted quad format
            end: Ip address in dotted quad format
        """
        if validate_cidr(start):
            # CIDR notation range
            start, end = cidr2block(start)

        elif end is None:
            if isinstance(start, tuple):
                # tuple range
                end = start(1)
                start = start(0)
            else:
                # degenerate range
                end = start

        start = ip2long(start)
        end = ip2long(end)
        self.startIp = min(start, end)
        self.endIp = max(start, end)
    #end __init__

    def __repr__ (self):
        """
        >>> print IpRange('127.0.0.1')
        ('127.0.0.1', '127.0.0.1')

        >>> print IpRange('10/8')
        ('10.0.0.0', '10.255.255.255')

        >>> print IpRange('127.0.0.255', '127.0.0.0')
        ('127.0.0.0', '127.0.0.255')
        """
        return (long2ip(self.startIp), long2ip(self.endIp)).__repr__()
    #end __repr__

    def __contains__ (self, item):
        """
        Implements membership test operators `in` and `not in` for the address 
        range.


        >>> r = IpRange('127.0.0.1', '127.255.255.255')
        >>> '127.127.127.127' in r
        True

        >>> '10.0.0.1' in r
        False

        >>> 2130706433L in r
        True

        >>> 'invalid' in r
        Traceback (most recent call last):
            ...
        TypeError: expected dotted-quad ip address or 32-bit integer


        Args:
            item: Dotted-quad ip address
        Returns:
            True if address is in range, False otherwise
        """
        if isinstance(item, basestring):
            item = ip2long(item)
        if type(item) not in [type(1), type(1L)]:
            raise TypeError, "expected dotted-quad ip address or 32-bit integer"

        return self.startIp <= item <= self.endIp
    #end __contains__

    def __iter__ (self):
        """
        Return an iterator over the range.


        >>> iter = IpRange('127/31').__iter__()
        >>> iter.next()
        '127.0.0.0'
        >>> iter.next()
        '127.0.0.1'
        >>> iter.next()
        Traceback (most recent call last):
            ...
        StopIteration
        """
        for i in xrange(self.startIp, self.endIp + 1):
            yield long2ip(i)
    #end __iter__
#end class IpRange

class IpRangeList (object):
    """
    List of IpRange objects.

    Converts a list of dotted quad ip address and/or CIDR addresses into a 
    list of IpRange objects. This list can perform ``in`` and ``not in`` tests 
    and iterate all of the addresses in the range.

    This can be used to convert django's conf.settings.INTERNAL_IPS list into 
    a smart object which allows CIDR notation.


    >>> INTERNAL_IPS = IpRangeList('127.0.0.1', '10/8', '192.168/16')
    >>> '127.0.0.1' in INTERNAL_IPS
    True
    >>> '10.10.10.10' in INTERNAL_IPS
    True
    >>> '192.168.192.168' in INTERNAL_IPS
    True
    >>> '172.16.0.1' in INTERNAL_IPS
    False
    """
    def __init__ (self, *args):
        self.ips = tuple(map(IpRange, args))
    #end __init__

    def __repr__ (self):
        """
        >>> print IpRangeList('127.0.0.1', '10/8', '192.168/16')
        (('127.0.0.1', '127.0.0.1'), ('10.0.0.0', '10.255.255.255'), ('192.168.0.0', '192.168.255.255'))
        """
        return self.ips.__repr__()
    #end __repr__

    def __contains__ (self, item):
        """
        Implements membership test operators `in` and `not in` for the address 
        range.


        >>> r = IpRangeList('127.0.0.1', '10/8', '192.168/16')
        >>> '127.0.0.1' in r
        True

        >>> '10.0.0.1' in r
        True

        >>> 2130706433L in r
        True

        >>> 'invalid' in r
        Traceback (most recent call last):
            ...
        TypeError: expected dotted-quad ip address or 32-bit integer


        Args:
            item: Dotted-quad ip address
        Returns:
            True if address is in range, False otherwise
        """
        for r in self.ips:
            if item in r:
                return True
        return False
    #end __contains__

    def __iter__ (self):
        """
        >>> iter = IpRangeList('127.0.0.1').__iter__()
        >>> iter.next()
        '127.0.0.1'
        >>> iter.next()
        Traceback (most recent call last):
            ...
        StopIteration

        >>> iter = IpRangeList('127.0.0.1', '10/31').__iter__()
        >>> iter.next()
        '127.0.0.1'
        >>> iter.next()
        '10.0.0.0'
        >>> iter.next()
        '10.0.0.1'
        >>> iter.next()
        Traceback (most recent call last):
            ...
        StopIteration
        """
        for r in self.ips:
            for ip in r:
                yield ip
    #end __iter__
#end class IpRangeList

def _test ():
    import doctest
    doctest.testmod()
#end _test

if __name__ == '__main__':
    _test()
# vim: set sw=4 ts=4 sts=4 et :
