#!/opt/rh/python27/root/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import os
import xml.etree.ElementTree as elementTree
import socks
import socket
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus


#https://na03.alma.exlibrisgroup.com/view/sru/[institution_code]?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma.other_system_number=ocm50774592&maximumRecords=3&startRecord=1

url = "https://na03.alma.exlibrisgroup.com/view/sru/[institution_code]?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma."

query = sys.argv[1]
search_term = sys.argv[2]

queryParams = urlencode({ query : search_term })
#socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
#socket.socket = socks.socksocket
request = Request(url + queryParams)

marcxml = urlopen(request).read()

print marcxml

print(url + queryParams)

#print url 

sys.exit()
