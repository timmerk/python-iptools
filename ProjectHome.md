A few useful functions and objects for manipulating ip addresses in python. This was all inspired by a desire to be able to use [CIDR](http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) address notation to designate INTERNAL\_IPS in a [Django](http://www.djangoproject.com/) project's settings file.

## Functions: ##
  * **validate\_ip**: Validate a dotted quad ip address.
  * **ip2long**: Convert a dotted quad ip address to a network byte order 32-bit integer.
  * **long2ip**: Convert a network byte order 32-bit integer to a dotted quad ip address.
  * **validate\_cidr**: Validate a CIDR notation ip address.
  * **cidr2block**: Convert a CIDR notation ip address into a tuple containing network block start and end addresses.

## Objects: ##
  * **IpRange**: Range of ip addresses providing ```in``` and iteration.
  * **IpRangeList**: List of IpRange objects providing ```in``` and iteration.

## Using with Django ##
The IpRangeList object can be used in a django settings file to allow CIDR notation and/or (start, end) ranges to be used in the INTERNAL\_IPS list.

### Example: ###
```
#!/usr/bin/env python
import iptools

INTERNAL_IPS = iptools.IpRangeList(
    '127.0.0.1',                # single ip
    '192.168/16',               # CIDR network block
    ('10.0.0.1', '10.0.0.19'),  # inclusive range
)
```

## Python Version Compatibility ##
This library has been tested with Python versions 2.3.5, 2.6.2, & 2.3.1 on Ubuntu x86\_64 and Python 2.6.1 & 2.6.4 on Snow Leopard.

## Installing ##
Install the latest stable version using easy\_install:
```
easy_install iptools
```
or pip:
```
pip install iptools
```

Install the latest development version:
```
git clone https://github.com/bd808/python-iptools.git
cd python-iptools
python setup.py install
```

## Contributing ##
Project development has moved to [GitHub](https://github.com/bd808/python-iptools). Feature requests, bug reports and pull requests are accepted there.