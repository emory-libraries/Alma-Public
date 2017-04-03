#!/bin/python
r'''
Title: Add Members
Contributors: Alex Cooper, Bernardo Gomez, Elizabeth Peele Mumpower
Date: 03/24/2017
Purpose: Add members to sets of item records in Alma
'''
import sys
import os
import re
from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode, quote_plus
import xml.etree.ElementTree as ET

def buildXml(barcodes):

    outcome = 1
    xml = "N/A"
    root = ET.Element("set")
    members = ET.SubElement(root, "members")
    for line in barcodes:
        line = str(line)
        line = line.rstrip("\n")
        member = ET.SubElement(members, "member")
        ids = ET.SubElement(member, "id").text = line
    try:
        xml = ET.tostring(root, encoding='utf-8', method='xml')
    except:
        sys.stderr.write("could not convert xml" + "\n")
    outcome = 0
    return xml,outcome

def main():

####<?xml version="1.0" encoding="UTF-8" standalone="yes"?><set><members><member><id>010000690077</id></member></members></set>
####1290788-1001
    if len(sys.argv) < 3:
        sys.stderr.write("system failure. arguments are missing." + "\n")
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
            if m.group(1) == "id_type":
                id_type = m.group(2)
            if m.group(1) == "op":
                op = m.group(2)
#   10671129920002486
    set_id = str(sys.argv[2])
    set_id = set_id.rstrip("\n")
    url = url.replace('{set_id}',quote_plus(set_id))
#    barcode = str("000007423101")
#    values = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><set><members><member><id>' + barcode + '</id></member></members></set>'
    try:
        values,outcome = buildXml(sys.stdin)
        print values
    except:
        sys.stderr.write("could not execute function" + "\n")
    try:
        queryParams = '?' + urlencode({ quote_plus('id_type') : id_type ,quote_plus('op') : op ,quote_plus('apikey') : apikey })
#        print url + queryParams
        headers = { 'Content-Type':'application/xml' }
        request = Request(url + queryParams
        , data=values
        , headers=headers)
        request.get_method = lambda: 'POST'
        response_body = urlopen(request).read()
#        print "hello"
        print response_body
    except HTTPError, e:
        message = e.read()
        print message
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
