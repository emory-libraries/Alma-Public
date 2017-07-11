#!/opt/rh/python27/root/usr/bin/python
r"""
Author: Alex Cooper
Title: Serials OCLC Holdings
Purpose: Check if OCLC holdings are set for deleted serials
Date: 07/05/2017
"""

import sys
import re
import requests
import socks
import socket
import xml.etree.ElementTree as ET

def get_item_info(result_node,id_list):

    outcome = 1
    try:
        rows = result_node.findall("Row")
    except:
        sys.stderr.write("could not find rows" + "\n")
        return id_list,outcome
    ocolc = re.compile("^\(OCoLC\)\d")
    ocn = re.compile("^ocn\d")
    ocm = re.compile("^ocm\d")
    oclc_no = "N/A"
    net_no = "N/A"
    collection = "N/A"
    info = "N/A"
    for row in rows:
        item_row = ""
        try:
            this_node = row.find("Column3")
            net_no = str(this_node.text)
            if ocm.match(net_no):
                oclc_no = net_no.strip( 'ocm' )
            elif ocn.match(net_no):
                oclc_no = net_no.strip( 'ocn' )
            elif ocolc.match(net_no):
                oclc_no = net_no.strip( '(OCoLC)' )
            else:
                continue
        except:
            sys.stderr.write("could not find network numbers" + "\n")
        try:
            this_node = row.find("Column2")
            collection = str(this_node.text)
        except:
            sys.stderr.write("could not find location" + "\n")
            return id_list,outcome
        info = str(oclc_no) + "	" + str(collection)
        outcome = 0
#        oclc_no = "12345678"
        id_list.append(info)
    return id_list,outcome

def main():

####process configuration file
    if len(sys.argv) < 2:
        sys.stderr.write("configuration file is missing" + "\n")
        return 1
    try:
        configuration = open(sys.argv[1], 'Ur')
    except:
        sys.stderr.write("could not open configuration file" + "\n")
    pat = re.compile("(.*?)=(.*)")
    for line in configuration:
        line = line.rstrip("\n")
        m = pat.match(line)
        if m:
            if m.group(1) == "url":
                url = m.group(2)
            if m.group(1) == "wskey":
                wskey = m.group(2)
            if m.group(1) == "location":
                location = m.group(2)
            if m.group(1) == "analytics_url":
                analytics_url = m.group(2)
            if m.group(1) == "path":
                path = m.group(2)
            if m.group(1) == "apikey":
                apikey = m.group(2)
            if m.group(1) == "limit":
                limit = m.group(2)
    configuration.close()
    """"
    print url
    print wskey
    print location
    print analytics_url
    print path
    print apikey
    print limit
    """
####make first analytics api call
    in_string = ""
    outcome = 1
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
    socket.socket = socks.socksocket
    payload = {'apikey':apikey,'path':path,'limit':limit}
    try:
        r = requests.get(analytics_url,params = payload)
    except:
        sys.stderr.write("api request failed" + "\n")
        return [],outcome
    return_code = r.status_code
    if return_code == 200:
        response = r.content
#        print response
    else:
        sys.stderr.write("analytics api failed (1)" + "\n")
        response = r.content
        sys.stderr.write(str(response) + "\n")
        return 1
    in_string = response
    in_string = in_string.replace("\n","")
    in_string = in_string.replace(" xmlns=\"urn:schemas-microsoft-com:xml-analysis:rowset\"","")
    try:
        tree = ET.fromstring(in_string)
    except:
        sys.stderr.write("parse analytics xml failed (1)" + "\n")
        return outcome
    try:
        finished = tree.find("QueryResult/IsFinished")
    except:
        sys.stderr.write("could not find finished (1)" + "\n")
        return outcome
    id_list = []
####start resumption loop
    if finished.text == "false":
        try:
            token = tree.find("QueryResult/ResumptionToken")
        except:
            sys.stderr.write("could not find resumption token" + "\n")
            return outcome
        this_token = str(token.text)
        sys.stderr.write(str(analytics_url) + " " + str(apikey) + " " + this_token + " " + str(id_list) + " " + limit + " " + "\n")
        try:
            result_node = tree.find("QueryResult/ResultXml/rowset")
        except:
            sys.stderr.write("could not find rowset (1)" + "\n")
            return outcome
        id_list,outcome = get_item_info(result_node,id_list)
        work_to_do = True
        outcome = 1
        while work_to_do:
         payload = {'apikey':apikey,'token':this_token,'limit':limit}
         try:
            r = requests.get(analytics_url,params = payload)
         except:
            sys.stderr.write("api request failed."+"\n")
            return outcome
         return_code = r.status_code
         if return_code == 200:
            response = r.content
         else:
            sys.stderr.write("FAILED(2)" + "\n")
            response = r.content
            sys.stderr.write(str(response) + "\n")
            return outcome
         in_string = response
         in_string = in_string.replace("\n","")
         in_string = in_string.replace(" xmlns=\"urn:schemas-microsoft-com:xml-analysis:rowset\"","")
         try:
              tree = ET.fromstring(in_string)
         except:
              sys.stderr.write("parse failed(1)."+"\n")
              return outcome
         try:
              finished = tree.find("QueryResult/IsFinished")
         except:
             sys.stderr.write("parse failed(2)."+"\n")
             return outcome
         if finished.text == "true":
             work_to_do = False
         try:
           result_node=tree.find("QueryResult/ResultXml/rowset")
         except:
            sys.stderr.write("couldn't find rowset."+"\n")
            return outcome
         if len(result_node) == 0:
            sys.stderr.write("empty result"+"\n")
            return 1
         id_list,outcome = get_item_info(result_node,id_list)
####make last analtics api call
    else:
        try:
            result_node = tree.find("QueryResult/ResultXml/rowset")
        except:
            sys.stderr.write("couldn't find rowset (0)" + "\n")
            return outcome
####    get oclc numbers and locations
        id_list,outcome = get_item_info(result_node,id_list)
    for ids in id_list:
####    check OCLC holdings information
        oclc_number = ""
        collections = ""
        infos = ids.split("	")
        oclc_number = infos[0]
        collections = infos[1]
        get_url = url + oclc_number
        payload = {'location':location,'wskey':wskey}
        try:
            r = requests.get(get_url,params = payload)
        except:
            sys.stderr.write("worldcat api failed" + "\n")
            return outcome
        return_code = r.status_code
        if return_code == 200:
            response = r.content
        else:
            sys.stderr.write("FAILED(3)" + "\n")
            response = r.content
            sys.stderr.write(str(response) + "\n")
            return outcome
        in_string = response
        in_string = in_string.replace("\n","")
        in_string = in_string.replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.loc.gov/standards/iso20775/N121_ISOholdings_v4.xsd"',"")
        try:
            tree = ET.fromstring(in_string)
        except:
            sys.stderr.write("could not read string" + "\n")
            return outcome
        try:
            inst_code = tree.findall("holding/institutionIdentifier/value")
        except:
            sys.stderr.write("could not get holding value" + "\n")
            return outcome
####    identify and report conflicts
        for code in inst_code:
            if code.text == "EMU":
                sys.stdout.write(code.text + "	" + "(OCoLC)" + ids + "\n")
            else:
                continue

if __name__=="__main__":
    sys.exit(main())
