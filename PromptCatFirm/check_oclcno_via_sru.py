#!/opt/rh/python27/root/usr/bin/python
# -*- coding: utf-8 -*-

r"""Title: marctxt_parser.py
Purpose: Parse marc.txt files / finite state machine example
Author: Alex C. (copied from Bernado's sketch)
Date: 09/07/2016"""

import sys
import re
import socks
import socket
import xml.etree.ElementTree as elementTree
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

####check for record with that oclc number in Alma
def check_oclc_numbers(oclc_no,query):
    outcome = 1
    url = "https://na03.alma.exlibrisgroup.com/view/sru/01GALI_EMORY?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma."
    oclc_no = str(oclc_no)
    queryParams = urlencode({ query : oclc_no })
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
    socket.socket = socks.socksocket
    try:
        request = Request(url + queryParams)
        result = urlopen(request).read()
    except:
        sys.stderr.write("no oclc no" + "\n")
    return result,0

####parse record with oclc number from Alma
def parse_xml(xml):

    outcome = 1
    try:
        xml = xml.replace("record xmlns=\"\"","record")
        xml = xml.replace(" xmlns=\"http://www.loc.gov/zing/srw/\"","")
        xml = xml.replace("\n","")
        tree=elementTree.fromstring(xml)
        check_result = tree.find("numberOfRecords")
        no_records = check_result.text
    except:
        sys.stderr.write("could not parse sru response" + "\n")
    try:
        record = tree.find("records/record/recordData/record")
        datafields = record.findall("datafield")
        for df in datafields:
            tag = df.get("tag")
            if tag == "245":
                subfields = df.findall("subfield")
                for sf in subfields:
                    code = sf.get("code")
                    if code == "a":
                        title = sf.text
                        outcome = 0
            else:
                continue
    except:
        sys.stderr.write("could not get title" + "\n")
    return title,no_records,outcome

def main():
    state = "init"
    rec_delimiter = "****"
    try:
#       process input
        for line in sys.stdin:
            line = line.rstrip('\n')
#           identify new record
            if state == "init":
                try:
                    if line[0:4] == rec_delimiter:
                        try:
                            state = "new"
                            delim = line
                            target = open('/tmp/ybp_sr_univ_duplicates.txt', 'w')
                        except:
                            sys.stderr.write("could not set state to new" + "\n")
                except:
                    sys.stderr.write("did not find delimiter")
#           process new record
            elif state == "new":
                if line[0:3] == "000":
                    ldr = line
                elif line[0:3] == "001":
                    oclc_no = line[8:20]
#                   check for possible duplicates
                    id_check,outcome = check_oclc_numbers(oclc_no,"other_system_number")
                    title,no_records,outcome = parse_xml(id_check)
                    if no_records != "0":
                        if title.isupper():
                            sys.stdout.write(delim + "\n")
                            sys.stdout.write(ldr + "\n")
                            sys.stdout.write(line + "\n")
                            state = "record"
                        elif not title.isupper():
                            target.write(delim + "\n")
                            target.write(ldr + "\n")
                            target.write(line + "\n")
                            state = "dups"
                    else:
                        sys.stderr.write("record with oclc number: " + oclc_no + "not in alma" + "\n")
#           continue processing records
            elif state == "record":
#               start new record
                if line[0:4] == rec_delimiter:
                    state = "new"
                else:
                    sys.stdout.write(line + "\n")
            elif state == "dups":
#               start new record
                if line[0:4] == rec_delimiter:
                    state = "new"
                else:
                    target.write(line + "\n")
    except:
        sys.stderr.write("error in input file" + "\n")

if __name__=="__main__":
    sys.exit(main())
