#!/bin/python
import sys
import cgi
import cgitb; cgitb.enable(display=1, logdir="/tmp")
import urllib2

def get_rdf(mmsid,inst):
    url = "https://open-na.hosted.exlibrisgroup.com/alma/" + inst + "/rda/entity/manifestation/" + mmsid + ".rdf"
    rdf = urllib2.urlopen(url).read()
    return rdf,url

def main():

    form = cgi.FieldStorage()
    target = open("/alma/webserver/docs/alma_rdf.html", 'rU')
    inst = form.getfirst('institution')
    mmsid = form.getfirst('mmsid')

    if len(form) == 0:
        print '%s' % "Content-Type: text/html; charset=utf-8"
        print ""
        for line in target:
            print line
        target.close()
    elif len(inst) == 0 or len(mmsid) == 0:
        print '%s' % "Content-Type: text/html; charset=utf-8"
        print ""
        for line in target:
            print line
        target.close()
    else:
        rdf,url = get_rdf(mmsid,inst)
        print '%s' % "Content-Type: text/html; charset=utf-8"
        print ""
        print "<xmp>"
        print str(rdf)
        print "</xmp>"

if __name__=="__main__":
    sys.exit(main())
