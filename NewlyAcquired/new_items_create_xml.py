#!/opt/rh/python27/root/usr/bin/python
# -*- coding: utf-8 -*-
r"""
   Program name: parse_new_items
   Author: Alex Cooper
   Date: june, 2016
   Purpose:
"""
import os
import sys
import re
import socks
import socket
import requests
import xml.etree.ElementTree as elementTree
import fnmatch

#9936572720402486|2016-08-01|2016-08-01|200000211735|None|22319416980002486|23319416960002486|

mmsid = []
item_creation = []
item_modification = []
barcode = []
process_type = []
try:
    previous_id = "0"
    print "<report>"
    print "<record>"
    for line in sys.stdin:
        parsed = line.split('|')
        mmsid = parsed[0]
        item_creation = parsed[1]
        item_modification = parsed[2]
        barcode = parsed[3]
        process_type = parsed[4]
        holding_id = parsed[5]
        item_id = parsed[6] 
        if mmsid == previous_id:
            copy_info = "<data_field>"+item_creation+"|"+item_modification+"|"+barcode+"|"+process_type+"|"+holding_id+"|"+item_id+"</data_field>"
            print copy_info
        else:
#            print "*****"
            print "</record>"
            print "<record>"
            print "<control_field>"+mmsid+"</control_field>"
            copy_info = "<data_field>"+item_creation+"|"+item_modification+"|"+barcode+"|"+process_type+"|"+holding_id+"|"+item_id+"</data_field>"
            print copy_info
            previous_id = mmsid
    print "</record>"
    print "</report>"
except:
    sys.stderr.write("could not parse line"+"\n")

sys.exit(
