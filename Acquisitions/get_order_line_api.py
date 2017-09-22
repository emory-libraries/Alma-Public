#!/bin/python

import sys
import requests
import xml.etree.ElementTree as ET

def parse_pol_xml(xml):

    outcome = 1
    tree = ET.fromstring(xml)
    pol_id = tree.find("number")
    pol_id = pol_id.text
    return pol_id,outcome

def main():

####process system argument
    po_line_id = sys.argv[1]
####read configuration file
    try:
        configuration = open("/sirsi/webserver/config/orders_api.cfg", "rU")
    except:
        sys.stderr.write("Could not open configuration file" + "\n")
####parse configuration file
    try:
        url = ""
        apikey = ""
        for line in configuration:
            line = line.rstrip("\n")
            line = line.split("=")
            if line[0] == "get_po_line_url":
                url = line[1]
            elif line[0] == "apikey":
                apikey = line[1]
            else:
                continue
    except:
        sys.stderr.write("Could not parse configuration file" + "\n")
####place API call
    try:
        url = url.replace("{po_line_id}", po_line_id)
        payload = {'apikey':apikey}
        r = requests.get(url, params = payload)
    except:
        sys.stderr.write("could not place API call" + "\n")
    return_code = r.status_code
    if return_code == 200:
        response = r.content
#        print response
    else:
        sys.stderr.write("Error placing API call" + "\n")
        response = r.content
        sys.stderr.write(str(response) + "\n")
    response,outcome = parse_pol_xml(response)
    print response

if __name__=="__main__":
    sys.exit(main())
