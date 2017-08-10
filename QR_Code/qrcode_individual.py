 #!/bin/env python
# -*- coding: utf-8 -*-
r"""
   qrcode_individual is a webservice that
   produces a qrcode for an ALMA item.
   it receives three variables:
      doc_id, callnum and library.
      doc_id is ALMA's mms_id;
      callnum is the item's call number;
      library is the item's holding library.
   qrcode_individual.py is the CGI script
   that uses the doc_id to retrieve the item's 
   title.
   the webservice writes a shortened title,
   the callnumber and the holding library code
   to the html page. the page contains a 
   javascript that generates the qrcode on the fly.
"""
__author__ = 'bernardo gomez'
__date__ = 'january 2016'

import os
import sys 
import cgi
import re
import marcxml
import requests
from datetime import date, datetime, time, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_record(base_url,docid):
   """
     it invokes custom webservice to get alma's MARCXML, including
     items.
     it returns two objects: 
        marcxml string and outcome (0=success, 1= failure)
   """
   xml_string=""
   outcome=1
   request_string=base_url+str(docid)
   try:
      r=requests.get(request_string, timeout=10)
   except:
      sys.stderr.write("api request failed.couldn't get bib record. \n")
      return xml_string,1
   status=r.status_code
   if status == 200:
       xml_string=r.content
   else:
       return xml_string,1
   return xml_string,0


def generate_qrcode(file,title,call_number,short_libname,library):
    """
       'file' is the html template.
       generate_qrcode inserts title, call_number 
       and abbreviated library name in the template.
       short_libname argument is a string with a list of library names.
       library argument is ALMA's library code.
    """
    library_name={}
    name_list=short_libname.split(";")
    for element in name_list:
        code,name=element.split(":")
        library_name[code]=name
    title=title[0:60]
    try:
       libr_name=library_name[library]
    except:
       libr_name=library

    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    print ""
    for line in file:
        line=line.replace(r"<!--CALL_NUMBER=-->",call_number)
        line=line.replace(r"<!--TITLE=-->",title)
        line=line.replace(r"<!--LIBRARY=-->",libr_name)
        print line

    return 0

def get_bib_title(docid,get_record_url):
   """
      it uses get_record_url webservice to 
      retrieve title that corresponds to docid.
   """ 
   #sys.stderr.write("here:"+str(docid)+" "+str(get_record_url)+"\n")
   title=""
   outcome=1
   try:
     xml_string,outcome=get_record(get_record_url,docid)
   except:
     sys.stderr.write("error getting xml:"+"\n")
     return "",1
   #sys.stderr.write("get_bib_title: "+str(outcome)+"\n")
   if outcome == 0:
     in_string=xml_string.replace("\n","")
     try:
         record=marcxml.biblio(in_string)
     except:
         sys.stderr.write("failed\n")
         return
     title_list=record.get_field("245")
     for title in title_list:
      title_part_a=""
      title_part_b=""
      subfield=title.split("\\p")
      title=""
      for sf in subfield:
         if sf != "":
            if sf[0:1] == "a":
                  #title_part_a=str(sf[1:])
                  title_part_a=sf[1:]
                  if title_part_a.isdigit():
                    title_part_a=str(title_part_a)
            if sf[0:1] == "b":
                  #title_part_b=str(sf[1:])
                  title_part_b=sf[1:]
                  if title_part_b.isdigit():
                    title_part_b=str(title_part_b)
      title=title_part_a+" "+title_part_b
      title=title.replace("/","")

   return title,outcome


def report_failure(code,description,doc_id):
 """
    it produces an error message in XML format.
 """
 print '%s' % "Content-Type: text/xml; charset=utf-8"
 print ""
 print '<?xml version="1.0"?>'
 print "<result>"
 print "<code>"+code+"</code>"
 print "<description>"+description+"</description>"
 print "<doc_id>"+str(doc_id)+"</doc_id>"
 print "</result>"
 return


def main():
   """
      CGI script that expects a configuration file
      on the command line.
      it receives HTTP variables 
      doc_id, callnum and library.
      it uses an html file as a template 
      to produce qrcode with (short) title,
      call number and holding library of
      a given item.
   """
   if len(sys.argv) < 2:
      sys.stderr.write("usage: config_file="+"\n")
      report_failure("ERROR","System failure. no configuration file.","")
      return 1

   doc_id=""
   input_page=""
   result_page=""
   get_record_url=""
   image=""
   short_libname=""

   try:
     configuration=open(sys.argv[1])
   except:
      report_failure("ERROR","System failure. couldn't open configuration file.","")
      return 1


   pat=re.compile("(.*?)=(.*)")
   for line in configuration:
      m=pat.match(line)
      if m:
         if m.group(1) == "input_page":
              input_page=m.group(2)
         if m.group(1) == "result_page":
              result_page=m.group(2)
         if m.group(1) == "failure_page":
              failure_page=m.group(2)
         if m.group(1) == "sys_email":
              sys_email=m.group(2)
         if m.group(1) == "get_record_url":
              get_record_url=m.group(2)
         if m.group(1) == "short_libname":
              short_libname=m.group(2)

   if sys_email== "":
     hostname=os.environ['WWW_HOST']
     sys_email="aleph"+"@"+hostname

   if get_record_url  == "":
      report_failure("ERROR","System failure. url for alma api is missing.","")
      return 1
   if input_page  == "":
      report_failure("ERROR","System failure. input file.","")
      return 1
   if result_page  == "":
      report_failure("ERROR","System failure. no result file.","")
      return 1
   if short_libname  == "":
      report_failure("ERROR","System failure. no short_libname.","")
      return 1

   try:
      inputf=open(input_page,"Ur")
   except:
      report_failure("ERROR","System failure. couldn't open form page.","")
      return 1

   try:
      resultf=open(result_page,"Ur")
   except:
      report_failure("ERROR","System failure. couldn't open result page.","")
      return 1

   form = cgi.FieldStorage()

   if len(form) == 0:
       report_failure("ERROR","unable to process request: doc_id is missing.","")
       return 1

   if  'doc_id' not in form:
      report_failure("ERROR","unable to process request: doc_id is missing","")
      return 1
   try:
       doc_id=form.getfirst('doc_id')
   except:
      report_failure("ERROR","unable to get doc_id.","")
      return 1

   if  'callnum' not in form:
      report_failure("ERROR","unable to process request: callnum is missing","")
      return 1
   try:
       callnum=form.getfirst('callnum')
   except:
      report_failure("ERROR","unable to get call number.","")
      return 1
   if  'library' not in form:
      report_failure("ERROR","unable to process request: library is missing","")
      return 1
   try:
       library=form.getfirst('library')
   except:
      report_failure("ERROR","unable to get library.","")
      return 1

   try:
       int(doc_id)
   except:
      report_failure("ERROR","doc_id is not an integer.","")
      return 1
       
   title,outcome=get_bib_title(str(doc_id),get_record_url)
   if outcome == 0:
       outcome=generate_qrcode(resultf,title,callnum,short_libname,library)
   else:
       report_failure("ERROR","get_bib_title failed:"+doc_id,"")

   return 0

if __name__=="__main__":
  sys.exit(main())
