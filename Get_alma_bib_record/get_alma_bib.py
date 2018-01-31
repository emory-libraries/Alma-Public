#!/bin/env python
# -*- coding: utf-8 -*-
"""
  Web service that receives a list of one or more alma mms_ids separated 
  by commas; it retrieves
  the bibliographic records from ALMA's api server, 
  and it displays
  the bibliograhic records to the web client in
  one of three formats: "xml", "marcedit" or "text".
  "xml" displays MARCXML;
  "text" format is home-grown display of MARC records developed by 
  bernardo gomez. the default format is xml.

  example of a request against emory's alma catalog:
  https://libapiproxyprod1.library.emory.edu/cgi-bin/get_alma_bib?doc_id=990022633760302486&format=marcedit 
  this program expects a configuration file, as a command line argument, with the following lines:
  sys_email= (if script reports fatal failures to admins. not used in this version.)
  api_host=https://api-na.hosted.exlibrisgroup.com
  apikey=<alma's apikey>


"""
__author__ = "bernardo gomez"
__date__ = " february 2016"

import os
import sys 
import re
import cgi
import cgitb; cgitb.enable(display=1, logdir="/tmp")
import requests
import xml.etree.ElementTree as elementTree
from datetime import date, timedelta


def google_analytics():
  """ for emory use only. 
      it inserts GA code.
      kristian needs this. 
  """
  print "<script>"
  print "window.ga=window.ga||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date; ga('create', 'UA-xxxxxx-23', 'auto');"

  print "ga('send', 'pageview');"
  print "</script>"
  print "<script async src='https://www.google-analytics.com/analytics.js'></script>"
  print "<script async src='https://template.library.emory.edu/js/plugins/analytics/autotrack/autotrack.js'></script>"
  return

###


def marcxml_to_marcedit(xml_string):
    """ it converts marcxml to terry reeses' application format, 
        see http://marcedit.reeset.net/features .
        it returns an empty string after a failure.
    """
    outcome=1
    text=""
    control_field=[]
    data_field=[]
    in_string=xml_string.replace("\n","")
    try:
       tree=elementTree.fromstring(in_string)
    except:
      sys.stderr.write("marcxml parse failed."+"\n")
      return text,outcome
    try:
       record_element=tree.find("record")
    except:
       sys.stderr.write("xml parsing failed. couldn't find record element"+"\n")
       return text,outcome
    try:
       leader=record_element.find("leader").text
       leader="^^^^^"+leader[5:]
       leader=leader.replace(" ","^")
       leader="=LDR  "+leader+"\n"
    except:
       sys.stderr.write("xml parsing failed. couldn't find leader"+"\n")
       return text,outcome
    try:
       controlfield_element=record_element.findall("controlfield")
    except:
       sys.stderr.write("xml parsing failed. couldn't find controlfield"+"\n")
       return text,outcome
    for cfield in controlfield_element:
       attribute=cfield.attrib
       try:
          value=str(cfield.text)
       except:
          value="FIX ME PLEASE"
       value=value.replace(" ","^")
       field="="+attribute['tag']+"  "+value
       control_field.append(field)
    try:
       datafield_element=record_element.findall("datafield")
    except:
       sys.stderr.write("xml parsing failed. couldn't find datafield"+"\n")
       return text,outcome

    try:
         for dfield in datafield_element:
                indicator1=str(dfield.get("ind1"))
                indicator2=str(dfield.get("ind2"))
                if indicator1 == " ":
                    indicator1="\\"
                if indicator2 == " ":
                    indicator2="\\"
                field_info="="+str(dfield.get("tag"))+"  "+indicator1+indicator2
                subfield=dfield.findall("subfield")
                field_text=""
                for subf in subfield:
                    for k in subf.attrib.keys():
                       try:
                         if subf.get(k) != "0":
                            #field_text=field_text+"$$"
                            field_text=field_text+"$"
                            field_text=field_text+subf.get(k)
                            try:
                                field_text=field_text+subf.text
                                #field_text=field_text.replace("&amp;","&")
                                #field_text=field_text.replace("&quot;","\"")
                                #field_text=field_text.replace("&apos;","'")
                                #field_text=field_text.replace("&lt;","<")
                                #field_text=field_text.replace("&gt;",">")
                            except:
                                pass
                       except:
                          sys.stderr.write("error in subfield\n")
                data_field.append(field_info+field_text)
                #print field_info+str(field_text)
    except:
       sys.stderr.write("xml parsing failed. couldn't find subfield"+"\n")
       return text,outcome
    text=leader
    for cf in control_field:
       text+=cf+"\n"
    for df in data_field:
       text+=df+"\n"
    #print text
    return text,0
    

def marcxml_to_text(xml_string):
    """ it converts marcxml to bernardo's format. 
        record delimiter is "******",
        subfield delimiter is "\\p"
        it returns an empty string after a failure.
    """
    outcome=1
    text=""
    control_field=[]
    data_field=[]
    in_string=xml_string.replace("\n","")
    try:
       tree=elementTree.fromstring(in_string)
    except:
      sys.stderr.write("marcxml parse failed."+"\n")
      return text,outcome
    try:
       record_element=tree.find("record")
    except:
       sys.stderr.write("xml parsing failed. couldn't find record element"+"\n")
       return text,outcome
    try:
       leader=record_element.find("leader").text
    except:
       sys.stderr.write("xml parsing failed. couldn't find leader"+"\n")
       return text,outcome
    try:
       controlfield_element=record_element.findall("controlfield")
    except:
       sys.stderr.write("xml parsing failed. couldn't find controlfield"+"\n")
       return text,outcome
    for cfield in controlfield_element:
       attribute=cfield.attrib
       try:
          value=str(cfield.text)
       except:
          value="FIX ME PLEASE"
       field=attribute['tag']+"||"+value
       control_field.append(field)
    try:
       datafield_element=record_element.findall("datafield")
    except:
       sys.stderr.write("xml parsing failed. couldn't find datafield"+"\n")
       return text,outcome

    try:
         for dfield in datafield_element:
                field_info=str(dfield.get("tag"))+"|"+str(dfield.get("ind1"))+str(dfield.get("ind2"))+"|"
                subfield=dfield.findall("subfield")
                field_text=""
                for subf in subfield:
                    for k in subf.attrib.keys():
                       try:
                         if subf.get(k) != "0":
                            #field_text=field_text+"$$"
                            field_text=field_text+"\\p"
                            field_text=field_text+subf.get(k)
                            try:
                                subfield_text=subf.text
                                if subfield_text.isdigit():
                                   subfield_text=str(subfield_text)
                                field_text=field_text+subfield_text
                                #sys.stderr.write(field_text+"\n")
                                #field_text=field_text.replace("&amp;","&")
                                #field_text=field_text.replace("&quot;","\"")
                                #field_text=field_text.replace("&apos;","'")
                                #field_text=field_text.replace("&lt;","<")
                                #field_text=field_text.replace("&gt;",">")
                            except:
                                pass
                       except:
                          sys.stderr.write("error in subfield\n")
                if field_text.isdigit():
                     field_text=str(field_text)
                #sys.stderr.write(field_info+field_text+"\n")
                data_field.append(field_info+field_text)
                #print field_info+str(field_text)
    except:
       sys.stderr.write("xml parsing failed. couldn't find subfield"+"\n")
       return text,outcome
    text="******\n"
    text+="000||"+leader+"\n"
    for cf in control_field:
       text+=cf+"\n"
    for df in data_field:
       text+=df+"\n"
    #print text
    return text,0



def get_bib_string(bib_xml):
   """ it receives an xml string and it adds the header to make it
       a marcxml string.
   """
   bib_string=""
   outcome=1
   in_string=bib_xml.replace("\n","")
   try:
      tree=elementTree.fromstring(in_string)
   except:
      sys.stderr.write("parse failed."+"\n")
      return bib_string,outcome

   try:
      bib_element=tree.find("record")
   except:
      sys.stderr.write("xml parsing failed. couldn't find record element"+"\n")
      return bib_string,outcome
   try:
       bib_string=elementTree.tostring(bib_element,encoding="utf-8",method="xml")
       #sys.stderr.write(str(bib_string)+"\n"))
       bib_string=bib_string.replace("<?xml version='1.0' encoding='utf-8'?>","")
       #bib_string=elementTree.tostring(bib_element,method="xml")
   except:
      sys.stderr.write("xml parsing failed. couldn't find record element"+"\n")
      return "",outcome
   bib_string=bib_string.replace(" schemaLocation=\"http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd\"","")
   bib_string=bib_string.replace("<leader>     ","<leader>12345")
   return bib_string,0

####

def api_request(host,request_data):
   """ 
     it performs a GET request through the url. url is composed of host
     and request_data. a correct response from ALMA's api server 
     produces a '200' return code.
   """
   response=""
   outcome=1
   url=host+request_data
   try:
      r=requests.get(url, timeout=10)
   except:
      sys.stderr.write("api request failed. \n")
      return response,1
   status=r.status_code
   if status == 200:
       response=r.content
   else:
       response="<result><code>ERROR</code></result>"
       return response,1
   return response,0


def print_result(result,out_type,alma_docid):
 """
  it prints a string that should go to the browser.
  string format depends on the output type.
 """
 if out_type == "xml":
    print result
    return 
 if out_type == "text":
     #sys.stderr.write("to_text\n")
     marc_text,outcome=marcxml_to_text(result)
     if outcome <> 0:
        print_text_error("unable to produce record","text",alma_docid)
        return 
 else:
    marc_text,outcome=marcxml_to_marcedit(result)
    if outcome <> 0:
        print_text_error("unable to produce record","marcedit",alma_docid)
        return 
 print "<pre>"+marc_text+"</pre>"

 return

def print_html_header():
    """
        hard-coded html header to display ALMA record 
        in text format.
    """
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    print "<!DOCTYPE html>"
    print "<html lang=\"en-US\">"
    print "<head>"
    print "<meta charset=\"utf-8\">"
    print "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
    print "<title>View Record</title>"
    google_analytics()
    print "</head>"
    print "<body>"
    return 0

def print_error(description):
 """
  it prints an xml page with an error message.
 """
 print '%s' % "Content-Type: text/xml; charset=utf-8"
 print ""
 print '<?xml version="1.0"?>'
 print "<ListErrors>"
 print "<error>"+description+"</error>"
 print "</ListErrors>"
 return

def print_xml_error(message,alma_docid):
   """
      it composes a MARCXML record with a title indicating a fatal ERROR.
   """
   print "<record><controlfield tag=\"001\">"+alma_docid+"</controlfield><datafield ind1=\"1\" ind2=\"0\" tag=\"245\"><subfield code=\"a\">"+message+"</subfield></datafield></record>"
   return 0

def print_text_error(message,out_type,alma_docid):
    """
      it composes a text record with a title indicating a fatal ERROR.
    """

    if out_type == "text":
      print "<pre>"
      print "*****"
      print "001||"+str(alma_docid)
      print "245|01|\\pa"+message
      print "</pre>"
    else:
      print "<pre>"
      print "=LDR  ^^^^^^^^^^^^^^^"
      print "=001  "+alma_docid
      print "=245  10$a"+message
      print "</pre>"
    return


def print_xml_record(api_host,request_string,alma_docid):
   """
       it retrieves an ALMA bib. record in XML format.
   """
   response,outcome=api_request(api_host,request_string)
   if outcome == 0:
         bib_string,outcome=get_bib_string(response)
         if outcome == 0:
                print_result(bib_string,"xml",str(alma_docid))
                return 0
         else:
            print_xml_error("bad record",alma_docid)
            return 1
   else:
         print_xml_error("ERROR: unable to get record",alma_docid)
         return 1

def print_text_record(api_host,request_string,out_type,alma_docid):
   """
      it retrieves an ALMA record in XML format and it invokes 
      a function to convert the XML format to text format.
      there are two text formats: "marcedit" and "text".
      terry reese created "marcedit",
      bernardo gomez created "text".
   """
   #sys.stderr.write(str(api_host)+request_string+" "+out_type+"\n")
   try:
# https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/"+str(mmsid)+"?apikey="+str(apikey),timeout=5)
           response,outcome=api_request(api_host,request_string)
           #sys.stderr.write(str(response)+"\n")
           if outcome == 0:
                 if out_type == "text":
                      print_result(response,"text",str(alma_docid))
                 else:
                      print_result(response,"marcedit",str(alma_docid))
           else:
               print_text_error("ERROR: failed to get bib record",out_type,alma_docid)
               return 1
   except:
           sys.stderr.write("api failed...\n")
           print_text_error("ERROR: ALMA API failed ",out_type,alma_docid)
           return 1
   return 0

def main():
   """
      function that performs the CGI tasks.
      it expects a configuration file the command line.
   """
   os.environ["LANG"]="en_US.utf8"
   if len(sys.argv) < 2:
      sys.stderr.write("usage: config_file="+"\n")
      print_error("system failure: no configuration file.")
      return 1
   
   item_string=""
   doc_id=""
   out_type="text"
   out_type="marcedit"
   out_type="xml"
#######
########
   doc_id="XXXXX"
   form = cgi.FieldStorage()
   if len(form) == 0:
       print_error("Expected doc_id.")
       return 1
   if 'format' in form:
        out_type = form.getfirst("format")
   if 'doc_id' in form:
        doc_id = form.getfirst("doc_id")
   try:
     config=open(sys.argv[1],'r')
   except:
      print_error("system failure: couldn't open config. file:"+sys.argv[1])
      sys.stderr.write("couldn't open config. file:"+sys.argv[1]+"\n")
      return 1
   sys_email="bgomez@emory.edu"
   apikey=""
   api_host=""
   param=re.compile("(.*)=(.*)")
   for line in config:
      line=line.rstrip("\n")
      m=param.match(line)
      if m:
         if m.group(1) == "sys_email":
            sys_email=m.group(2)
         if m.group(1) == "apikey":
            apikey=str(m.group(2))
         if m.group(1) == "api_host":
            api_host=str(m.group(2))
   config.close()

   if apikey == "":
      print_error("apikey is missing in configuration file.")
      return 1
   if api_host == "":
      print_error("api hostname is missing in configuration file.")
      return 1
   #doc_id="9936579694202486,9936573007602486"
   #doc_id="8936579694202486,8936573007602486"
   doc_id=doc_id.replace(" ","")
   doclist=doc_id.split(",")
   if out_type == "xml":
      print '%s' % "Content-Type: text/xml; charset=utf-8"
      print ""
      bib_string="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+"<collection xmlns=\"http://www.loc.gov/MARC21/slim\">"
      print bib_string
      for alma_docid  in doclist:
        request_string="/almaws/v1/bibs/"+str(alma_docid)+"?apikey="+str(apikey)
        outcome=print_xml_record(api_host,request_string,str(alma_docid))
      print "</collection>"
   else:
      print_html_header()
      for alma_docid  in doclist:
         try:
            int(alma_docid)
         except:
           print_error("doc_id must be a number")
           return 1
         request_string="/almaws/v1/bibs/"+str(alma_docid)+"?apikey="+str(apikey)
         outcome=print_text_record(api_host,request_string,out_type,str(alma_docid))
      print "</body>"
      print "</html>"

   return 0


if __name__=="__main__":
  sys.exit(main())
