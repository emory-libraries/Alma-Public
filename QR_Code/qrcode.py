#!/bin/env python
# -*- coding: utf-8 -*-
r"""
    webservice that receives a list of alma mms_ids and
    presents a form with a list of corresponding items.
    the webservice assumes that mms_ids belong to 
    physical items. that is, they have a physical location.
    the user may select one item to get a qr_code.
    the qr_code contains the holding library, the callnumber and 
    a shortened title of the item.
    the webservice expects a configuration file
    on the command line with the following variables:
    baseurl=
    failure_page=
    get_record_url=
    input_page=
    result_page=

"""
__author__ = 'bernardo gomez'
__date__ = 'january 2016'

import os
import sys 
import cgi
import re
import marcxml
import urllib
import requests 
from datetime import date, datetime, time, timedelta
import xml.etree.ElementTree as elementTree

def  display_html_notrequestable(record_title,doc_id,error_message):
   """
      it displays an html page with an error message when
      there are no elegible physical items.
   """
   print '%s' % "Content-Type: text/html; charset=utf-8"
   print ""

   print "<!DOCTYPE html>"
   print "<html lang=\"en-US\">"
   print "<head>"

   print "<title>No physical items</title><h3>No physical items.</h3>"
   print  "<style>a.menu_xml_http{font-weight:bold;}</style>"
   print  "<meta charset=\"utf-8\">"
   print  "<meta name=\"viewport\" content=\"width=device-width\">"
   print   "<meta name=\"Keywords\" content=\"\">"
   print   "<meta name=\"Description\" content=\"\">"
   print   "<link rel=\"icon\" href=\"/favicon.ico\" type=\"image/x-icon\">"

   print  "<style type=\"text/css\">"

   print  "</style>"


   print "</head>"
   print "<body>"
   print  "<hr>"
   print  "<p>"
   print  error_message
   print "<p>"


   print "</body>"
   print  "</html>"
   return 0


def  one_item(baseurl,doc_id,requestable):
   """
      this function directs request to a specific target, via
      a "Location:" HTTP header.
      it is used to handle a request with a single elegible 
      item.
   """
   library_name={'UNIV':'WOODRUFF-MAIN','HLTH':'HEALTH','THEO':'THEOLOGY','OXFD':'OXFORD','MARBL':'MARBL',
        'BUS':'BUSINESS','MUS':'MUSIC&MEDIA'}
   callnum_encode="NONE"
   copy=requestable[0]
   lib_code=copy[0]
   try:
       libr_name=library_name[lib_code]
   except:
       libr_name=lib_code
   if copy[1] != "":
      callnum_encode=copy[1]
   url=baseurl+"/qrcode_individual?doc_id="+str(doc_id)+"&callnum="+callnum_encode+"&library="+libr_name
   sys.stdout.write("Location: "+url+"\n\n")
   return 0


def display_html_failure(record_title,message):
   """
       it displays an html page with an error message,
       as a result of a fatal failure.
   """
   print '%s' % "Content-Type: text/html; charset=utf-8"
   print ""

   print "<!DOCTYPE html>"
   print "<html lang=\"en-US\">"
   print "<head>"

   print "<title>Failure</title><h3>Unable to display title.</h3>"
   print  "<style>a.menu_xml_http{font-weight:bold;}</style>"
   print  "<meta charset=\"utf-8\">"
   print  "<meta name=\"viewport\" content=\"width=device-width\">"
   print   "<meta name=\"Keywords\" content=\"\">"
   print   "<meta name=\"Description\" content=\"\">"
   print   "<link rel=\"icon\" href=\"/favicon.ico\" type=\"image/x-icon\">"

   print  "<style type=\"text/css\">"

   print  "</style>"


   print "</head>"

   print "<body>"
   print  "<hr>"
   print  "<p>"
   print  message
   print "<p>"


   print "</body>"
   print  "</html>"
   return 0



def display_html_page(record_title,requestable,input_page,doc_id):
    """
       it displays an html page with a list of elegible items to 
       receive a qrcode.
       function searches <!--table_starts_here--> as a marker
       to insert the list.
       
    """
    library_name={'UNIV':'WOODRUFF-MAIN','HLTH':'HEALTH','THEO':'THEOLOGY','OXFD':'OXFORD','MARBL':'MARBL',
        'BUS':'BUSINESS','MUS':'MUSIC&MEDIA'}
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    found_title=False
    current_libr="--"
    first_library=True
    callnum_encode=""
    if len(requestable) > 1:
          sorted_items=sorted(requestable,key=lambda library: library[0])
#MARBL|STACK|ISSBD|XE102 .A3 V.47 1961|010001131422|available|
    else:
          sorted_items=requestable
    for line in input_page:
       line=line.rstrip("\n")
       table=re.search("<!--table_starts_here-->", line)
       found_title=re.search("<!--TITLE=-->", line)
       if table:
          print "<table>"
          for copy in sorted_items:
              #sys.stderr.write("copy:"+str(copy)+"\n")
              callnum=copy[1]
              callnum_encode=urllib.quote(callnum)
              lib_code=copy[0]
              try:
                libr_name=library_name[lib_code]
              except:
                libr_name=lib_code

              url="/cgi-bin/qrcode_individual?doc_id="+str(doc_id)+"&callnum="+callnum_encode+"&library="+libr_name
              if copy[0] <> current_libr:
                 if first_library:
                     print "<tr><td nowrap colspan=1 align=left>Items belonging to: <b>"+copy[0]+"</b></td></tr>"
                     first_library=False
                     current_libr=copy[0]
                     ####print "<tr><td nowrap align=left>"+copy[1]+"</td><td align=left><a href=\"javascript:open_win('"+copy[2]+"')\">Request it</a><td></tr>"
                     print "<tr><td nowrap align=left>"+copy[1]+"</td><td align=left><a href=\""+url+"\">Display QR code</a><td></tr>"
                 else:
                     print "<tr><td colspan=2><hr></td></tr>"
                     print "<tr><td></td></tr>"
                     print "<tr><td nowrap colspan=1 align=left>Items belonging to: <b>"+copy[0]+"</b></td></tr>"
                     current_libr=copy[0]
                     ###print "<tr><td nowrap align=left>"+copy[1]+"</td><td align=left><a href=\"javascript:open_win('"+copy[2]+"')\">Request it</a><td></tr>"
                     print "<tr><td nowrap align=left>"+copy[1]+"</td><td align=left><a href=\""+url+"\">Display QR code</a><td></tr>"
              else:
                     print "<tr><td nowrap align=left>"+copy[1]+"</td><td align=left><a href=\""+url+"\">Display QR code</a><td></tr>"
          print "</table>"
       elif found_title:
          line=line.replace("<!--TITLE=-->",record_title)
          print line
       else:
          print line
    return 0



def get_items(xml_string):
   """
      it receives a MARCXML string in
      xml_string and it extracts
      the items held in "999" fields.
   """
   items=[]
   outcome=1
   in_string=xml_string.replace("\n","")
   try:
       record=marcxml.biblio(in_string)
   except:
       sys.stderr.write("failed\n")
       return
   copies=record.get_field("999")
#01|holding-library|location|material-type|
   for copy in copies:
      subfield=copy.split("\\p")
      material_type="xxxx"
      location="xxxx"
      library="xxxx"
      callnumber="xxxx"
      barcode="xxxx"
      available="xxxx"
      for sf in subfield:
         if sf != "":
            if sf[0:1] == "l":
                  location=str(sf[1:])
            elif sf[0:1] == "t":
                  material_type=str(sf[1:])
            elif sf[0:1] == "m":
                  library=(sf[1:])
            elif sf[0:1] == "a":
                  callnumber=(sf[1:])
            elif sf[0:1] == "i":
                  barcode=(sf[1:])
            elif sf[0:1] == "b":
                  available=(sf[1:])
      copy_info=library+"|"+location+"|"+material_type+"|"+callnumber+"|"+str(barcode)+"|"+available+"|"
      
      #sys.stderr.write(str(copy_info)+"\n")
      items.append(copy_info)
   return items,0


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


def get_bib_title(xml_string):
   """
     it receives a MARCXML string in xml_string
     and it extracts the bibliographic title
     held in the "245" field.
   """
   title=""
   outcome=0
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
                  title_part_a=sf[1:]
                  if title_part_a.isdigit():
                      title_part_a=str(title_part_a)
            if sf[0:1] == "b":
                  title_part_b=sf[1:]
                  if title_part_b.isdigit():
                      title_part_b=str(title_part_b)
      title=title_part_a+" "+title_part_b
      title=title.replace("/","")
      #title=urllib.quote(title)
      #print "title:"+title

   return title,0


def display_electronic_title(html,title,url):
    """
      this function is not used in this version.
      it might become handy to handle
      a doc_id for a portfolio (no physical items)
      whose qrcode would contain a URL to an 
      electronic resource.
    """
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    for line in html:
      line=line.replace("<!--TITLE=-->",title)
      line=line.replace("<!--URL=-->",url)
      sys.stdout.write(line)
    return 0

def report_failure(code,description,doc_id):
 """
    it displays an error message in an XML object.

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
      in the command line.
      it receives an ALMA mms_id in the HTTP variable 'doc_id'.
      if the record corresponding to the doc_id has multiple 
      items, script will produce an html page with a menu;
      if the record has only one item, then the script will
      redirect to request to webservice that produces the
      qrcode for the corresponding item.
   """
   if len(sys.argv) < 2:
      sys.stderr.write("usage: config_file="+"\n")
      report_failure("ERROR","System failure. no configuration file.","")
      return 1

   doc_id=""
   input_page=""
   result_page=""
   get_record_url=""
   baseurl="http://mail.library.emory.edu/uhtbin"
   try:
     configuration=open(sys.argv[1],"Ur")
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
         if m.group(1) == "get_record_url":
             get_record_url=m.group(2)
         if m.group(1) == "baseurl":
              baseurl=m.group(2)


   if input_page  == "":
      report_failure("ERROR","System failure. input file.","")
   if result_page  == "":
      report_failure("ERROR","System failure. no result file.","")
      return 1
   if baseurl  == "":
      report_failure("ERROR","System failure. no baseurl","")
      return 1
   if get_record_url  == "":
      report_failure("ERROR","System failure. no get_record_url","")
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
       docids=form.getfirst('doc_id')
   except:
      report_failure("ERROR","unable to get doc_id.","")
      return 1
   #docids="990029398460302486,990001182920302486,9936499776502486,990017507910302486,990006103010302486"
   docid_list=docids.split(",")
   for doc_id in docid_list:
     try:
        doc_id=int(doc_id)
     except:
######
       report_failure("ERROR","doc_id is not an integer.","")
       return 1
       
   #doc_id="{:09d}".format(doc_id)
####
   requestable=[]
   for doc_id in docid_list:
     try:
       items=[]
       try:
           xml_string,outcome=get_record(get_record_url,doc_id)
       except:
             sys.stderr.write("item_info retrieval failed:"+"\n")
             report_failure("FAILURE","get_record failed:"+doc_id,"")
             return 1
       if outcome == 0:
          items,outcome=get_items(xml_string)
       else:
          items=[]
       #sys.stderr.write(str(items)+"\n")
       for i_info in items:

                   i_field=i_info.split("|")
                   item_to_display=[]
                   try:
                           item_to_display.append(str(i_field[0]))
                           item_to_display.append(str(i_field[3]))
                           requestable.append(item_to_display)
                   except:
                       sys.stderr.write("failed"+"\n")
                       display_html_failure("","unable to process request: system failure(3)")
                       return 1

     except:
      display_html_failure("","unable to process request: system failure,,")
      return 1

   record_title,outcome=get_bib_title(xml_string)
   if len(requestable) > 1:
       display_html_page(record_title,requestable,inputf,doc_id)
       for req_item in requestable:
           noop=1
           #sys.stderr.write("requestable:"+str(req_item)+"\n")
      
       #report_success("OK","**=UNDER CONSTRUCTION**",doc_id,user_id,"BOOK","")
   elif len(requestable) == 1:
       one_item(baseurl,doc_id,requestable)
       return 0

   else:
       error_message="<p>This title exists in electronic form only.</p>"
       display_html_notrequestable(record_title,doc_id,error_message)
   inputf.close()
   return 0



if __name__=="__main__":
  sys.exit(main())
  
