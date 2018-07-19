#!/opt/rh/python27/root/usr/bin/python
r"""
Author: Alex Cooper
Title: MARCXML Parser
Date: 07/18/2018
Purpose: Parse MARCXML
"""
import sys
import xml.etree.ElementTree as ET

def parse_items(df):

    barcode = ""
    material_type = ""
    desc = ""
    call_no = ""
    library = ""
    location = ""
    delim = "|"
    subfield = df.findall("subfield")
    for sf in subfield:
        code = sf.get("code")
        if code == "a":
            barcode = str(sf.text)
        if code == "b":
            material_type = str(sf.text)
        if code == "c":
            desc = str(sf.text)
        if code == "f":
            call_no = sf.text
        if code == "d":
            library = sf.text
        if code == "e":
            location = sf.text
        item = library + delim + location + delim + barcode + delim + material_type + delim + call_no + delim + desc
    return item

def parse_record(record):

    outcome = 1
    mmsid = ""
    item_form = ""
    title = ""
    delim = "|"
    items = []
    rows = []
    controlfield = record.findall("controlfield")
    datafield = record.findall("datafield")
    for cf in controlfield:
        tag = cf.get("tag")
        if tag == "001":
            mmsid = str(cf.text)
        if tag == "008":
            item_form = str(cf.text[23])
    for df in datafield:
        tag = df.get("tag")
        if tag == "245":
            subfield = df.findall("subfield")
            for sf in subfield:
                code = sf.get("code")
                if code == "a":
                    title = sf.text
        if tag == "999":
            item = parse_items(df)
            items.append(item)
    for item in items:
        rows.append(mmsid + delim + item_form + delim + title + delim + item)
    return rows

def main():

    delim = "|"
    marc_xml = sys.stdin.read()
    tree = ET.fromstring(marc_xml)
    records = tree.findall("record")
    print "MMSID" + delim + "FORM OF ITEM" + delim + "TITLE" + delim + "LIBRARY" + delim + "LOCATION" + delim + "BARCODE" + delim + "MATERIAL TYPE" + delim + "CALL NUMBER" + delim + "DESCRIPTION"
    for record in records:
        rows = parse_record(record)
        for row in rows:
            print row

if __name__=="__main__":
    sys.exit(main())
