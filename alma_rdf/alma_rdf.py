#!/bin/python
import sys
import cgi
import cgitb; cgitb.enable(display=1, logdir="/tmp")
import urllib2
r'''
Title: Alma RDF
Purpose: Retrieve Alma records in RDF
Author: Alex Cooper
Date: 12/27/2017
'''

def get_bibframe(mmsid,inst):
    url = "https://open-na.hosted.exlibrisgroup.com/alma/" + inst + "/bf/entity/instance/" + mmsid
    bibframe = urllib2.urlopen(url).read()
    return bibframe,url

def get_jsonld(mmsid,inst):
    url = "https://open-na.hosted.exlibrisgroup.com/alma/" + inst + "/bibs/" + mmsid + ".jsonld"
    jsonld = urllib2.urlopen(url).read()
    return jsonld,url

def get_rdf(mmsid,inst):
    url = "https://open-na.hosted.exlibrisgroup.com/alma/" + inst + "/rda/entity/manifestation/" + mmsid + ".rdf"
    rdf = urllib2.urlopen(url).read()
    return rdf,url

def main():

    form = cgi.FieldStorage()
    target = open("/alma/webserver/docs/alma_rdf.html", 'rU')
    inst = form.getfirst('institution')
    mmsid = form.getfirst('mmsid')
    rec_format = form.getfirst('format')

    if len(form) == 0 or len(mmsid) == 0:
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
        if rec_format == 'bibframe':
            bibframe,url = get_bibframe(mmsid,inst)
            print '%s' % "Content-Type: text/html; charset=utf-8"
            print ""
            print "<xmp>"
            print str(bibframe)
            print "</xmp>"
        elif rec_format  == 'jsonld':
            jsonld,url = get_jsonld(mmsid,inst)
            print '%s' % "Content-Type: text/html; charset=utf-8"
            print ""
            print "<xmp>"
            print str(jsonld)
            print "</xmp>"
        elif rec_format  == 'rdf':
            rdf,url = get_rdf(mmsid,inst)
            print '%s' % "Content-Type: text/html; charset=utf-8"
            print ""
            print "<xmp>"
            print str(rdf)
            print "</xmp>"

if __name__=="__main__":
    sys.exit(main())
