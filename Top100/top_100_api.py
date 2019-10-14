#!/opt/rh/python27/root/usr/bin/python
'''
Title: Most Used Reports API
Purpose: publish html of the reports to /alma/webserver/docs/
Author: Alex C.
Date: 01/30/2017
Requires: Python2.7
'''
import sys
import re
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus
import xml.etree.ElementTree as elementTree

def main():
####https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports?path=/shared/Emory%20University%20Libraries/Reports/ACOOPE5/mostPopularPhilosophy&apikey=
    url = ""
    apikey = ""
    path = ""
    limit = ""
    elements_list = []
    try:
        configuration = open(sys.argv[1], 'rU')
    except:
        sys.stderr.write("configuration file is missing." + "\n")
        return 1
    try:
        pat = re.compile("(.*?)=(.*)")
        try:
            for line in configuration:
                line = line.rstrip("\n")
                m = pat.match(line)
                try:
                    if m:
                        if m.group(1) == "url":
                            url = m.group(2)
                        if m.group(1) == "apikey":
                            apikey = m.group(2)
                        if m.group(1) == "path":
                            path = m.group(2)
                        if m.group(1) == "limit":
                            limit = m.group(2)
                except:
                    sys.stderr.write("could not find match." + "\n")
        except:
            sys.stderr.write("could not parse configuration file." + "\n")
        configuration.close()
    except:
        sys.stderr.write("could not apply regex." + "\n")
    try:
        queryParams = '?' + urlencode({ quote_plus('path') : path ,quote_plus('apikey') : apikey ,quote_plus('limit') : limit })
        request = Request(url + queryParams)
####        print url + queryParams
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
####        sys.stdout.write(response_body + "\n")
    except:
        sys.stderr.write("could not execute analytics api query(1)." + "\n")
    try:
        in_string = response_body
        in_string = in_string.replace("\n","")
        in_string = in_string.replace(" xmlns=\"urn:schemas-microsoft-com:xml-analysis:rowset\"","")
    except:
        sys.stderr.write("could not modify xml string." + "\n")
    try:
        tree = elementTree.fromstring(in_string)
    except:
        sys.stderr.write("could not read xml string." + "\n")
    try:
        result_node = tree.find("QueryResult/ResultXml/rowset")
    except:
        sys.stderr.write("could not find rowset." + "\n")
    mms_id = ""
    title = ""
    author = ""
    isbn = ""
    loans = ""
    try:
        rows = result_node.findall("Row")
    except:
        sys.stderr.write("could not get rows." + "\n")
    try:
        for this_row in rows:
            isbn = ""
            try:
                this_node = this_row.find("Column1")
                author = str(this_node.text)
####                print "<h1>" + author + "</h1>"
            except:
                sys.stderr.write("could not get author." + "\n")
            try:
                this_node = this_row.find("Column8")
                isbn = str(this_node.text)
#                isbn = isbn.split("; ")[0]
####        "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn
            except:
                sys.stderr.write("could not get isbn." + "\n")
            try:
                this_node = this_row.find("Column3")
                mms_id = str(this_node.text)
####                print "<p class=center>" + "<a href=\"http://discovere.emory.edu/primo_library/libweb/action/dlSearch.do?institution=EMORY&vid=discovere&query=any,exact," + mms_id + "\"" + " style=\"color:#000000\">" + "<h1>" + title + " " + author + "</h1>" + "</a>" + "</p>"
            except:
                sys.stderr.write("could not get mmsId" + "\n")
            try:
                this_node = this_row.find("Column4")
                title = str(this_node.text)
####                print "<p class=center>" + "<h1>" + title + " " + author + "</h1>" + "</p>"
            except:
                sys.stderr.write("could not get title for " + mms_id + "\n")
            try:
                this_node = this_row.find("Column9")
                loans = str(this_node.text)
####                <img src="http://covers.openlibrary.org/b/isbn/9780812993547-M.jpg">
####                print "<p class=center>" + "<a href=\"http://discovere.emory.edu/primo_library/libweb/action/dlSearch.do?institution=EMORY&vid=discovere&query=any,exact," + mms_id + "\"" + " style=\"color:#000000\">" + "<h1>" + title + " " + author + "</h1>" + "</a>" + "<b style=\"padding-left: 1em;\">" + loans + " loans" + "</b>" + "</p>"
                sys.stdout.write("									<p class=center>" + "<a href=\"http://discovere.emory.edu/primo_library/libweb/action/dlSearch.do?institution=EMORY&vid=discovere&query=any,exact," + mms_id + "\"" + " style=\"color:#000000\">" + "<h1>" + title + " " + author + "</h1>" + "</a>" + "<img src=\"http://covers.openlibrary.org/b/isbn/" + isbn + "-M.jpg\">" + "<b style=\"padding-left: 1em;\">" + loans + " loans" + "</b>" + "</p>" + "\n")
            except:
                sys.stderr.write("could not get loans" + "\n")
    except:
        sys.stderr.write("could not parse rows." + "\n") 

if __name__=="__main__":
    sys.exit(main())
