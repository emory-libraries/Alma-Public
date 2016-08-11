#!/usr/bin/python
r'''
Title: new_items 2.1
Putpose: find new items in house xml
Authors: Alex C.
Date: 07/07/2016
'''

import sys
import re
import os
import datetime as dt
import xml.etree.ElementTree as elementTree

marcXml = sys.stdin.read()
yesterday = str(dt.date.today() - dt.timedelta(1))
#print yesterday
try:
    tree = elementTree.fromstring(marcXml)
except:
    sys.stderr.write("bad input"+"\n")
try:
    record = tree.findall("record")
except:
    sys.stderr.write("failed to parse xml"+"\n")
for rec in record:
    status = "NEW"
    try:
        sysno = rec.find("control_field")
        sys_no = str(sysno.text)
#        print sys_no
    except:
        sys.stderr.write("no sys number"+"\n")
        continue
    try:
        item_info = rec.findall("data_field")
        for info in item_info:
            try:
                item = str(info.text)
                item = item.split('|')
                creation_date = str(item[0])
                process = str(item[3])
                barcode = str(item[2])
                holding_id = str(item[4])
                item_id = str(item[5])
#                print creation_date
#                print yesterday
#                print process
                if str(creation_date) == str(yesterday):
#                    print sys_no+" "+str(item[2])+" "+str(item[0])
                    status = "NEW"
                    try:
                        if process == "Acquisition":
                            status = "In Process"
                        elif process == "In Process":
                            status = "In Process"
                        elif process == "Missing":
                            status = "In Process"
                        elif process == "Requested":
                            status = "In Process"
                    except:
                        sys.stderr.write("no process"+"\n")
                else:
#                    print "old"
#                    print sys_no+" "+"old"
#                    print creation_date+" "+yesterday
                    status = "OLD"
                    break
            except:
                sys.stderr.write("could not parse item info"+"\n")
    except:
        sys.stderr.write("no item info"+"\n")
        continue
#    try:
    if status == "NEW":
        print sys_no+"|"+status+"|"
    elif status == "In Process":
        print sys_no+"|"+status+"|"+barcode+"|"+holding_id+"|"+item_id+"|"
#    except:
#        sys.stderr.write("no status"+"\n")
#        continue

sys.exit()
