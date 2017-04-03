#!/bin/python
r'''
Title: Run Delete Job
Contributors: Alex Cooper
Date: 04/01/2017
Purpose: Run job to deleteo a set of item records in Alma
'''
import sys
import os
import re
from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode, quote_plus
import xml.etree.ElementTree as ET

def main():

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
    set_id = str(sys.argv[2])
    set_id = set_id.rstrip("\n")
    values = '<job><parameters><parameter><name>task_WithdrawItemsParams_boolean</name><value>DELETE_HOL_BIB</value></parameter><parameter><name>do_not_delete_items_with_active_requests_isSelected</name><value>false</value></parameter><parameter><name>do_not_delete_items_with_not_yet_active_requests_isSelected</name><value>false</value></parameter><parameter><name>do_not_delete_items_with_work_orders_isSelected</name><value>false</value></parameter><parameter><name>set_id</name><value>' + set_id + '</value></parameter><parameter><name>job_name</name><value>Withdraw items - via API - delete_me</value></parameter></parameters></job>'
    try:
        queryParams = '?' + urlencode({ quote_plus('op') : 'run' ,quote_plus('apikey') : apikey })
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
