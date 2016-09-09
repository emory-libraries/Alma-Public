#!/opt/rh/python27/root/usr/bin/python
# -*- coding: utf-8 -*-

r"""Title: marctxt_parser.py
Purpose: Parse marc.txt files / finite state machine example
Author: Alex C. (copied from Bernado's sketch)
Date: 09/07/2016"""

import sys
import re
import xml.etree.ElementTree as elementTree
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

####check for record with that oclc number in Alma
def check_oclc_numbers(oclc_no,query):
    institution = ""
    outcome = 1
    url = "https://na03.alma.exlibrisgroup.com/view/sru/" + institution + "?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma."
    oclc_no = str(oclc_no)
    queryParams = urlencode({ query : oclc_no })
    try:
        request = Request(url + queryParams)
        result = urlopen(request).read()
    except:
        sys.stderr.write("no oclc no" + "\n")
    return result,0

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
                            target = open('/tmp/duplicates.txt', 'a')
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
                    try:
                        id_check=id_check.replace("record xmlns=\"\"","record")
                        id_check=id_check.replace(" xmlns=\"http://www.loc.gov/zing/srw/\"","")
                        id_check=id_check.replace("\n","")
                        tree=elementTree.fromstring(id_check)
                        check_result = tree.find("numberOfRecords")
                        no_records = check_result.text
                    except:
                        sys.stderr.write("could not parse sru response" + "\n")
                    if no_records != "0":
                        target.write(delim + "\n")
                        target.write(ldr + "\n")
                        target.write(line + "\n")
                        state = "dups"
                    else:
                        sys.stdout.write(delim + "\n")
                        sys.stdout.write(ldr + "\n")
                        sys.stdout.write(line + "\n")
                        state = "record"
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
