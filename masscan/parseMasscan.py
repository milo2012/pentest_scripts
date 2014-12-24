#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import os
import sys
from collections import defaultdict as ddict
try:
    from defusedxml.ElementTree import parse
except ImportError:
    print("defusedxml not found, downgrading to builtin XML parsing library.")
    from xml.etree.ElementTree import parse

if sys.argv[1] is None:
    raise SystemExit("need a file to convert")
if not os.path.exists(sys.argv[1]):
    raise SystemExit("File {} does not exist".format(sys.argv[1]))

# keep file name, to use for outputs
name = os.path.splitext(sys.argv[1])[0]

# parse file, extract hosts, map by open port found
et = parse(sys.argv[1])
et.findall('host')
xhosts = et.findall('host')
portmap = ddict(list)
for xhost in xhosts:
    _hostaddr = xhost.getchildren()[0].items()[1][1]
    _port = xhost.getchildren()[1].getchildren()[0].items()[1][1]
    portmap[_port].append(_hostaddr)

# dump to files corresponding to each port name
for port, hosts in portmap.iteritems():
    outname = '{}-port{}.list'.format(name, port)
    with open(outname, 'w') as ofd:
        for host in hosts:
            ofd.write('{}\n'.format(host))
    print("wrote {}".format(outname))
