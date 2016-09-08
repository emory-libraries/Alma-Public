#!/bin/python
# -*- coding: utf-8 -*-

r"""Title: marctxt_parser.py
Purpose: Parse marc.txt files / finite state machine example
Author: Alex C. (copied from Bernado's sketch)"""

import sys
import re
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

####check for record with that oclc number in Alma
def check_oclc_numbers(oclc_no,query):
    insitution = [] #enter institution code
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
                            print line
                        except:
                            sys.stderr.write("could not set state to new" + "\n")
                except:
                    sys.stderr.write("did not find delimiter")
#           process new record
            elif state == "new":
                if line[0:3] == "001":
                    print line
                    oclc_no = line[8:20]
                    print oclc_no
                    state = "record"
#           continue processing record
            elif state == "record":
                if line[0:3] == "035":
                    print line
                elif line[0:3] == "245":
                    print line
#               start new record
                elif line[0:4] == rec_delimiter:
                    print line
                    state = "new"
    except:
        sys.stderr.write("error in input file" + "\n")

if __name__=="__main__":
    sys.exit(main())
