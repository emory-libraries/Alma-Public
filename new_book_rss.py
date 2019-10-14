#!/usr/bin/python
import sys
import xml.etree.ElementTree as ET
import requests
r""""Author: Alex Cooper
Date: 07/02/2019
Title: Publish Alma RSS Feed as HTML
Requires: Python2.7"""

def parse_xml(xml):

    tree = ET.fromstring(xml.content)
    channel = tree.find("channel")
    items = channel.findall("item")
    datastring = []
    for item in items:
        title = item.find("title")
        title = title.text
        title = title.rstrip(" /")
        link = item.find("link")
        link = link.text
        author = item.find("author")
        if author is not None:
            author = author.text
        else:
            author = "N/A"
        description = item.find("description")
        description = description.text
        language = item.find("language")
        language = language.text
        form = item.find("format")
        if form is not None:
            form = form.text
        else:
            form = "N/A"
        mattype = item.find("mattype")
        if mattype is not None:
            mattype = mattype.text
        else:
            mattype = "N/A"
        arrival = item.find("arrivalDate")
        arrival = arrival.text
        linked_title = title + "|" + link + "|" + author + "|" + description + "|" + language + "|" + form + "|" + mattype + "|" + arrival
        datastring.append(linked_title)
    return datastring

def main():

    r = requests.get("https://na03.alma.exlibrisgroup.com/rep/getFile?institution_code=01GALI_EMORY&file=newBooks&type=RSS")
    result = parse_xml(r)
    data_piece = ""
    for x in result:
        x = x.split("|")
        title = x[0]
        link = x[1]
        author = x[2]
        data_piece = data_piece + '<p><a href="' + link + '">' + title + '</a></p>' + '<p>' + author + '</p><br/>'
    data_set = '<!DOCTYPE html><html><body>' + data_piece + '</body></html>'
    print data_set

if __name__=="__main__":
    sys.exit(main())
