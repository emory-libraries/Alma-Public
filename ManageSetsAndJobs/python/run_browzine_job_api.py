#!/bin/python
r'''
Title: Run Browzine Job
Contributors: Alex Cooper
Date: 06/21/2017
Purpose: Run job to update Browzine's database
'''
import sys
import os
import re
from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode, quote_plus
import xml.etree.ElementTree as ET

def main():

    if len(sys.argv) < 2:
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
'''
Testing xml
'''
    values = '<job><parameters><parameter><name>task_ExportBibParams_outputFormat_string</name><value>GOOGLE_SCHOLAR</value></parameter><parameter><name>task_ExportBibParams_maxSize_string</name><value>0</value></parameter><parameter><name>task_ExportBibParams_exportFolder_string</name><value>PRIVATE</value></parameter><parameter><name>task_ExportParams_ftpConfig_string</name><value>3814963300002486</value></parameter><parameter><name>task_ExportParams_ftpSubdirectory_string</name><value></value></parameter><parameter><name>task_ExportParams_interfaceName</name><value>true</value></parameter><parameter><name>task_ExportParams_filterInactivePortfolios</name><value>false</value></parameter><parameter><name>task_ExportParams_baseUrl</name><value/></parameter><parameter><name>set_id</name><value>3052579090002486</value></parameter><parameter><name>job_name</name><value>Export Electronic Portfolios - via API - ejournals test</value></parameter></parameters></job>'
'''
Production xml
'''
###    values = '<job><parameters><parameter><name>task_ExportBibParams_outputFormat_string</name><value>GOOGLE_SCHOLAR</value></parameter><parameter><name>task_ExportBibParams_maxSize_string</name><value>0</value></parameter><parameter><name>task_ExportBibParams_exportFolder_string</name><value>PRIVATE</value></parameter><parameter><name>task_ExportParams_ftpConfig_string</name><value>4289509490002486</value></parameter><parameter><name>task_ExportParams_ftpSubdirectory_string</name><value></value></parameter><parameter><name>task_ExportParams_interfaceName</name><value>true</value></parameter><parameter><name>task_ExportParams_filterInactivePortfolios</name><value>false</value></parameter><parameter><name>task_ExportParams_baseUrl</name><value/></parameter><parameter><name>set_id</name><value>6210743680002486</value></parameter><parameter><name>job_name</name><value>Export Electronic Portfolios - via API - JSTOR EJournals</value></parameter></parameters></job>'
    try:
        queryParams = '?' + urlencode({ quote_plus('op') : 'run' ,quote_plus('apikey') : apikey })
        headers = { 'Content-Type':'application/xml' }
        request = Request(url + queryParams
        , data=values
        , headers=headers)
        request.get_method = lambda: 'POST'
        response_body = urlopen(request).read()
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
