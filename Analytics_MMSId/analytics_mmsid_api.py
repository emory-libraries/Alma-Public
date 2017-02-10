#!/opt/rh/python27/root/usr/bin/python
'''
Title: Analytics MMSId
Purpose: produce a file of mmsIds from an analytics report
Author: Alex C.
Date: 02/10/2016
'''
import sys
import re
import socks
import socket
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus
import xml.etree.ElementTree as elementTree

def get_mmsId(result_node,id_list):
    mms_id = ""
    outcome = 1
    try:
        rows = result_node.findall("Row")
    except:
        sys.stderr.write("could not find Rows." + "\n")
    for r in rows:
        try:
            this_node = r.find("Column1")
            mms_id = str(this_node.text)
            outcome = 0
        except:
            sys.stderr.write("could not find mmsId." + "\n")
            mms_id = "N/A"
        id_list.append(mms_id) 
    return id_list,outcome

def main():
    url = ""
    apikey = ""
    path = ""
    limit = ""
    in_string = ""
    id_list = []
    try:
        configuration = open(sys.argv[1], 'rU')
    except:
        sys.stderr.write("configuration file is missing." + "\n")
        return 1
    try:
        pat = re.compile("(.*?)=(.*)")
        try:
            for line in configuration:
                line = line.rstrip("\n")
                m = pat.match(line)
                try:
                    if m:
                        if m.group(1) == "url":
                            url = m.group(2)
                        if m.group(1) == "apikey":
                            apikey = m.group(2)
                        if m.group(1) == "path":
                            path = m.group(2)
                        if m.group(1) == "limit":
                            limit = m.group(2)
                except:
                    sys.stderr.write("could not find match." + "\n")
        except:
            sys.stderr.write("could not parse configuration file." + "\n")
        configuration.close()
    except:
        sys.stderr.write("could not apply regex." + "\n")
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
    socket.socket = socks.socksocket
    try:
        queryParams = '?' + urlencode({ quote_plus('path') : path ,quote_plus('apikey') : apikey ,quote_plus('limit') : limit })
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
#        print response_body
    except:
        sys.stderr.write("could not execute analytics api query(1)." + "\n")
    try:
        in_string = response_body
        in_string = in_string.replace("\n","")
        in_string = in_string.replace(" xmlns=\"urn:schemas-microsoft-com:xml-analysis:rowset\"","")
    except:
        sys.stderr.write("could not edit analytics query(1)." + "\n")
    try:
        tree = elementTree.fromstring(in_string)
    except:
        sys.stderr.write("could not read string (1)." + "\n")
    try:
        finished = tree.find("QueryResult/IsFinished")
    except:
        sys.stderr.write("parse failed (1)." + "\n")
    if finished.text == "false":
        try:
            token = tree.find("QueryResult/ResumptionToken")
        except:
            sys.stderr.write("parse failed (2)." + "\n")
        this_token = str(token.text)
        try:
            result_node = tree.find("QueryResult/ResultXml/rowset")
        except:
            sys.stderr.write("could not find rowset." + "\n")
        id_list,outcome = get_mmsId(result_node,id_list)
        work_to_do = True
        outcome = 1
        while work_to_do:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
            socket.socket = socks.socksocket
            try:
                queryParams = '?' + urlencode({ quote_plus('apikey') : apikey ,quote_plus('token') : this_token ,quote_plus('limit') : limit })
                request = Request(url + queryParams)
                request.get_method = lambda: 'GET'
                response_body = urlopen(request).read()
            except:
                sys.stderr.write("could not execute analytics api query(2)." + "\n")
                return 1
            try:
                in_string = response_body
                in_string = in_string.replace("\n","")
                in_string = in_string.replace(" xmlns=\"urn:schemas-microsoft-com:xml-analysis:rowset\"","")
            except:
                sys.stderr.write("could not edit analytics query(2)." + "\n")
            try:
                tree = elementTree.fromstring(in_string)
            except:
                sys.stderr.write("could not read string (2)>" + "\n")
            try:
                finished = tree.find("QueryResult/IsFinished")
            except:
                sys.stderr.write("parse failed 2." + "\n")
            if finished.text == "true":
                work_to_do = False
            try:
                result_node = tree.find("QueryResult/ResultXml/rowset")
            except:
                sys.stderr.write("could not find rowset." + "\n")
            id_list,outcome = get_mmsId(result_node,id_list)
    else:
        try:
            result_node = tree.find("QueryResult/ResultXml/rowset")
        except:
            sys.stderr.write("could not find rowset." + "\n")
        id_list,outcome = get_mmsId(result_node,id_list)
    for ids in id_list:
        sys.stdout.write(ids + "\n")

if __name__=="__main__":
    sys.exit(main())
