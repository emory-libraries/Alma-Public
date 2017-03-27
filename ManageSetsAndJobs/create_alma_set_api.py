#!/bin/python
r'''
Title: Create Sets In Alma
Author: Alex Cooper
Date: 03/23/2017
Purpose: Create sets of item records in Alma
'''
import sys
import os
import re
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus
import xml.etree.ElementTree as ET

def main():

    if len(sys.argv) < 2:
        sys.stderr.write("system failure. configuration file is missing." + "\n")
        return 1
    try:
        configuration = open(sys.argv[1], 'rU')
    except:
        sys.stderr.write("could not read configuration file " + sys.argv[1] + "\n")
    pat = re.compile("(.*?)=(.*)")
    for line in configuration:
        line = line.rstrip("\n")
        m = pat.match(line)
        if m:
            if m.group(1) == "url":
                url = m.group(2)
            if m.group(1) == "apikey":
                apikey = m.group(2)
    set_xml = str('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><set link="/almaws/v1/conf/sets/6491540120001021"><name>AGCTesting02</name><type desc="Itemized">ITEMIZED</type><content desc="Physical items">ITEM</content><private desc="Yes">true</private><status desc="Active">ACTIVE</status><created_by>1004968</created_by></set>')
    try:
        queryParams = '?' + urlencode({ quote_plus('apikey') : apikey })
        values = set_xml
        headers = { 'Content-Type':'application/xml' }
        request = Request(url + queryParams
        , data=values
        , headers=headers)
        request.get_method = lambda: 'POST'
        response_body = urlopen(request).read()
#        print response_body
    except:
        sys.stderr.write("could not call url" + "\n")
    try:
        tree = ET.fromstring(response_body)
        ids = tree.find('id')
        ids = ids.text
        sys.stdout.write(ids + "\n")
    except:
        sys.stderr.write("could not parse xml" + "\n")

if __name__=="__main__":
    sys.exit(main())
