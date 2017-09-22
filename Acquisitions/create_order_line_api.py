#!/bin/python

import sys
import requests
import xml.etree.ElementTree as ET

def create_order_line(xml):

    outcome = 1
    return xml,outcome

def main():

    order_xml = open("/sirsi/webserver/integrations/acquisitions/files/create_order.xml", "rU")
####read configuration file
    try:
        configuration = open("/sirsi/webserver/config/orders_api.cfg", "rU")
    except:
        sys.stderr.write("Could not open configuration file" + "\n")
####parse configuration file
    try:
        for line in configuration:
            line = line.rstrip("\n")
            line = line.split("=")
            if line[0] == "post_po_line_url":
                url = line[1]
            elif line[0] == "apikey":
                apikey = line[1]
            else:
                continue
    except:
        sys.stderr.write("Could not parse configuration file" + "\n")
####prepare order line xml
    response,outcome = create_order_line(order_xml)
    print response.read()

if __name__=="__main__":
    sys.exit(main())
