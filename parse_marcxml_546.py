#!/usr/bin/python
import xml.etree.ElementTree as ET
import sys
r"""
Title: Parse MARCXML For 001, 245, and 546
Author: Alex Cooper
Purpose: Print MMSID, Title, 546a and 546b
Date: 06/15/2018
"""

def main():

    tree = ET.fromstring(sys.stdin.read())
    records = tree.findall("record")
    print("mmsid" + "|" + "title" + "|" + "546a" + "|" + "546b")
    for record in records:
        tite = mmsid = ""
        lang_a = []
        lang_b = []
        control = record.findall("controlfield")
        for cf in control:
            tag = cf.get("tag")
            if tag == "001":
                mmsid = cf.text
        datafields = record.findall("datafield")
        for df in datafields:
            tag = df.get("tag")
            if tag == "245":
                subfields = df.findall("subfield")
                for sf in subfields:
                    code = sf.get("code")
                    if code == "a":
                        title = sf.text
            elif tag == "546":
                subfields = df.findall("subfield")
                for sf in subfields:
                    code = sf.get("code")
                    if code == "a":
                        lang_a.append(sf.text)
                    elif code == "b":
                        lang_b.append(sf.text)
#        print(lang_b)
        print(mmsid + "|" + title + "|" + str(lang_a) + "|" + str(lang_b))

if __name__=="__main__":
    sys.exit(main())
