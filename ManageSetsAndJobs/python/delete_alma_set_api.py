#!/bin/python
r'''
Title: Delete Sets In Alma
Author: Alex Cooper
Date: 03/23/2017
Purpose: Delete sets of item records in Alma
'''
import sys
import os
import re
from urllib2 import Request, urlopen, HTTPError
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
    set_id = str(sys.stdin.read())
    set_id = set_id.rstrip("\n")
    url = url.replace('{set_id}',quote_plus(set_id))
#    print url
    try:
        queryParams = '?' + urlencode({ quote_plus('apikey') : apikey })
        request = Request(url + queryParams)
        print url + queryParams
        request.get_method = lambda: 'DELETE'
        response_body = urlopen(request).read()
#        print response_body
    except HTTPError, e:
        message = e.read()
        in_string = message
        in_string = in_string.replace("\n", "")
        in_string = in_string.replace(" xmlns=\"http://com/exlibris/urm/general/xmlbeans\"", "")
        tree = ET.fromstring(in_string)
        errorMessage = tree.find('errorList/error/errorMessage')
        errorMessage = errorMessage.text
        sys.stderr.write("HTTPError: " + str(errorMessage) + "\n")
    configuration.close()

if __name__=="__main__":
    sys.exit(main())
