#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Web service that receives an alma mms_id; it retrieves
  the bibliographic record and the associated copies from ALMA's 
  api server;  and it displays the consolidated record to 
  the web client in one of three formats: "xml", "marcedit" or "text".
  "text" format is home-grown display of MARC records developed by 
  bernardo gomez. the default format is xml.
  example of a request against emory's alma catalog:
  https://libapiproxyprod1.library.emory.edu/cgi-bin/get_alma_record?doc_id=990022633760302486&format=marcedit 
  this program expects a configuration file, as a command line argument, with the following lines:
  sys_email= (if script reports fatal failures to admins. not used in this version.)
  api_host=https://api-na.hosted.exlibrisgroup.com
  apikey=<alma's apikey>

  __author__ = "bernardo gomez"
  __date__ = " february 2016"

"""

import os
import sys 
import re
import cgi
import cgitb; cgitb.enable(display=1, logdir="/tmp")
import requests
import xml.etree.ElementTree as elementTree
from datetime import date, timedelta


def api_request(host,request_data):

   """ it performs a GET request through the url. 
       url is composed of host and request_data. a 
       correct response from ALMA's api server 
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

def api_direct(url):

   """ it performs a GET request through the url. 
       a correct response from ALMA's api server 
       produces a '200' return code.
   """
   response=""
   outcome=1
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


def get_item_string(item_xml):
    """
       it receives an xml string from ALMA api server for a
       given holding record. it parses xml to produce
       copy information in marcxml format.
       the copy metadata is presented as MARCXML "999" datafield.
       it returns three variables:
           marcxml string,
           count of copies, and
           outcome (0=success, 1=failure)
    """
    outcome=1
    count=0
    item_info=""

    available="unavailable"
    enumeration_a=""
    chronology_i=""
    description=""
    library=""
    physical_material_type=""
    policy=""
    location=""
    process_type=""
    callnumber=""
    callnumber_type=""
    pid=""

    in_string=item_xml.replace("\n","")
    try:
      tree=elementTree.fromstring(in_string)
    except:
      sys.stderr.write("parse failed."+"\n")
      return item_info,count,outcome
    try:
       total_item_count=tree.get("total_record_count")
       #sys.stderr.write("total_item:"+str(total_item_count)+"\n")
    except:
      sys.stderr.write("xml parsing failed. couldn't find items element"+"\n")
      return item_info,count,outcome
    try:
       item_list=tree.findall("item")
    except:
      sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
      return item_info,count,outcome

    for item_element in item_list:
       count+=1
       try:
         callnum_element=item_element.find("holding_data/call_number")
         if callnum_element is None:
            callnumber=""
         else:
            callnumber=callnum_element.text
            if callnumber is None:
              callnumber=""
         callnumber=callnumber.replace("&","&amp;")
         callnumber=callnumber.replace("\"","&quot")
         callnumber=callnumber.replace("'","&apos")
         callnumber=callnumber.replace("<","&lt;")
         callnumber=callnumber.replace(">","&gt;")
       except:
         sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
         return item_info,count,outcome
       try:
          callnum_type_element=item_element.find("holding_data/call_number_type")
       except:
          sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
          return item_info,outcome,outcome
       callnumber_type=callnum_type_element.text
       if callnumber_type is None:
          callnumber_type=""
       try:
         item_element=item_element.find("item_data")
       except:
         sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
         return item_info,count,outcome
       try:
         pid=item_element.find("pid").text
         if pid is None:
            pid=""
       except:
         sys.stderr.write("xml parsing failed. couldn't find pid element"+"\n")
         return item_info,count,outcome
       try:
          barcode=item_element.find("barcode").text
          if barcode is None:
             barcode=""
       except:
         sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
         return item_info,count,outcome
       try:
          available_element=item_element.find("base_status").text
           
          if available_element is None:
            available="unavailable"
          else:
             if available_element == "1":
                available="available"
             else:
                available="unavailable"

       except:
         sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
         return item_info,count,outcome

       try:
          enumeration_a=item_element.find("enumeration_a").text
          if enumeration_a is None:
             enumeration_a=""
       except:
          sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
          return item_info,count,outcome
       try:
          chronology_i=item_element.find("chronology_i").text
          if chronology_i is None:
              chronology_i=""
       except:
         sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
         return item_info,count,outcome
       try:
          description=item_element.find("description").text
          if description is None:
              description=""
          description=description.replace("&","&amp;")
          description=description.replace("\"","&quot")
          description=description.replace("'","&apos")
          description=description.replace("<","&lt;")
          description=description.replace(">","&gt;")
       except:
          sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
          return item_info,count,outcome
       try:
          library=item_element.find("library").text
          if library is None:
             library=""
       except:
          sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
          return item_info,count,outcome
       try:
          location=item_element.find("location").text
          if location is None:
             location=""
       except:
         sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
         return item_info,count,outcome
       try:
          process_type=item_element.find("process_type").text
          if process_type is None:
             process_type=""
       except:
         sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
         return item_info,count,outcome
       try:
          physical_material_type=item_element.find("physical_material_type").text
          if physical_material_type is None:
              physical_material_type=""
       except:
         sys.stderr.write("xml parsing failed. couldn't find material type element"+"\n")
         return item_info,count,outcome
       try:
          policy=item_element.find("policy").text
          if policy is None:
              policy=""
       except:
         sys.stderr.write("xml parsing failed. couldn't find policy element"+"\n")
         return item_info,count,outcome
       if description != "":
           callnumber+=" "+str(description)
       
       item_info+="<datafield ind1=\" \" ind2=\" \" tag=\"999\"><subfield code=\"a\">"+callnumber+"</subfield>"+"<subfield code=\"b\">"+available+"</subfield>"+"<subfield code=\"d\">"+str(description)+"</subfield>"+"<subfield code=\"e\">"+str(pid)+"</subfield>"+"<subfield code=\"f\">"+str(process_type)+"</subfield>"+"<subfield code=\"i\">"+str(barcode)+"</subfield>"+"<subfield code=\"l\">"+location+"</subfield>"+"<subfield code=\"m\">"+library+"</subfield>"+"<subfield code=\"p\">"+str(policy)+"</subfield>"+"<subfield code=\"t\">"+physical_material_type+"</subfield>"+"<subfield code=\"w\">"+str(callnumber_type)+"</subfield></datafield>"
    return item_info,count,0


def get_total(item_xml):
    """ it receives an xml string for a given item and it extracts
        the item count from the "total_record_count" element.
        it returns two variables:
           item_count and
           outcome (0=success, 1=failure)
    """
    total_item_count=0

    in_string=item_xml.replace("\n","")
    try:
      tree=elementTree.fromstring(in_string)
    except:
      sys.stderr.write("parse failed."+"\n")
      return total_item_count,1
    try:
       total_item_count=tree.get("total_record_count")
       #sys.stderr.write("total_item:"+str(total_item_count)+"\n")
    except:
      sys.stderr.write("xml parsing failed. couldn't find items element"+"\n")
      return total_item_count,1
    return total_item_count,0

def get_item_info(url,count,item_info,offset):
    """
       it receives the url of the next set of items,
       the set size (count), 
       the offset of the set in the total batch,
       and the current xml string containing the
       copies retrieved so far.
    """
    url_pattern=re.compile("(.*?)&offset=(.*)")
    m=url_pattern.match(url)
    if m:
       url=m.group(1)+"&offset="+str(offset)

    #sys.stderr.write("url:"+url+"\n")
    response,outcome=api_direct(url)
    #print response
    if outcome == 0:
       total_count,outcome=get_total(response)
       
       if outcome == 0:
         if int(count) >= int(total_count):
            return item_info,offset,outcome
         else:
          # produce item_info
            item_string,batch_size,outcome=get_item_string(response)
            item_info+=item_string
            count+=batch_size
            offset=count
            if int(offset) >= int(total_count):
               return item_info,offset,outcome
            item_info,offset,outcome=get_item_info(url,count,item_info,offset)
       else:
           item_info=""
           offset=""
           outcome=1
    return item_info,offset,outcome


def marcxml_to_marcedit(xml_string):
    """
       it converts a MARCXML string to terry resee's marcEdit format.
       example of output:

       =LDR  ^^^^^cpca^2200517Ii^4500
       =001  990029881400302486
       =008  110425i19282009gau^^^^^^^^^^^^^^^^^eng^d
       =035  \\$a(OCoLC)714621339
       =100  1\$aWright, Sarah E.
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
    """
       it converts a MARCXML string to bernardo gomez's text format.
       example of output:
       ******
       000|  |05285cpca 2200517Ii 4500
       001|  |990029881400302486
       008|  |110425i19282009gau                 eng d
       035|  |\pa(Aleph)002988140EMU01
       100|1 |\paWright, Sarah E.
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
       field=attribute['tag']+"|  |"+value
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
    text+="000|  |"+leader+"\n"
    for cf in control_field:
       text+=cf+"\n"
    for df in data_field:
       text+=df+"\n"
    #print text
    return text,0

def get_docid(xml_string):
    """
      it parses an xml_string recturned by 
      /almaws/v1/items?item_barcode="+str(item_id)
      and it extracts the mms_id of the bibliographic record.
    """
    doc_id=""
    outcome=1
    in_string=xml_string.replace("\n","")
    try:
      tree=elementTree.fromstring(in_string)
    except:
      sys.stderr.write("parse failed."+"\n")
      return doc_id,outcome
    try:
       bib_element=tree.find("bib_data")
    except:
      sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
      return doc_id,outcome
    try:
       doc_id=bib_element.find("mms_id").text
    except:
       doc_id,outcome

    return doc_id,0   



def get_holding_list(holding_xml):
   """
     it parses the xml returned by
     /almaws/v1/bibs/alma_docid/holdings
     and returns a list of links to ALMA holding records.
   """
   holding_list=[]
   outcome=1
   in_string=holding_xml.replace("\n","")
   try:
      tree=elementTree.fromstring(in_string)
   except:
      sys.stderr.write("parse failed."+"\n")
      return holding_list,outcome
   try:
      holdings=tree.findall("holding")
   except:
      sys.stderr.write("xml parsing failed. couldn't find holding element"+"\n")
      return holding_list,outcome
   for h_element in holdings:
      try:
          holding_link=h_element.get("link")
          holding_list.append(holding_link)
      except:
          sys.stderr.write("xml parsing failed. couldn't find link attribute."+"\n")
          return holding_link,outcome
   return holding_list,0


def get_bib_string(bib_xml):
   """
      this function extracts the bibliographic record from
      the XML string returned by ALMA's API. ALMA's 
      MARCXML record is enclosed by markup
       <collection xmlns="http://www.loc.gov/MARC21/slim">
         <record></record>
       </collection>
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
   bib_string=bib_string.replace("</record>","")
   bib_string=bib_string.replace("<leader>     ","<leader>12345")
   return bib_string,0


def print_result(result,out_type):
 """
  it prints xml or html with record in text format.
  it invokes one of the following functions:
      marcxml_to_text or
      marcxml_to_marcedit .
      the default output is MARCXML.
 """
 if out_type == "xml":
    print '%s' % "Content-Type: text/xml; charset=utf-8"
    #print '%s' % "Access-Control-Allow-Origin: http://emory-primosb-alma.hosted.exlibrisgroup.com"
    print '%s' % "Access-Control-Allow-Origin: *"
    print '%s' % "Access-Control-Allow-Methods: GET"
    print ""
    print result
    return 
 if out_type == "text":
     #sys.stderr.write("to_text\n")
     marc_text,outcome=marcxml_to_text(result)
 else:
    marc_text,outcome=marcxml_to_marcedit(result)
 if outcome == 0:
       print '%s' % "Content-Type: text/html; charset=utf-8"
       #print '%s' % "Access-Control-Allow-Origin: http://emory-primosb-alma.hosted.exlibrisgroup.com"
       print '%s' % "Access-Control-Allow-Origin: *"
       print '%s' % "Access-Control-Allow-Methods: GET"
       print ""
       print "<!DOCTYPE html>"
       print "<html lang=\"en-US\">"
       print "<head>"
       print "<title>View Record</title>"
       print "</head>"
       print "<body>"
       print "<pre>"+marc_text+"</pre>"
       print "</body>"
       print "</html>"
 else:
       print '%s' % "Content-Type: text/html; charset=utf-8"
       #print '%s' % "Access-Control-Allow-Origin: http://emory-primosb-alma.hosted.exlibrisgroup.com"
       print '%s' % "Access-Control-Allow-Origin: *"
       #print '%s' % "*"
       print '%s' % "Access-Control-Allow-Methods: GET"
       print ""
       print "<!DOCTYPE html>"
       print "<html lang=\"en-US\">"
       print "<head>"
       print "<title>ERROR</title>"
       print "</head>"
       print "<body>"
       print "<pre>"+"failure"+"</pre>"
       print "</body>"
       print "</html>"

 return

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


def main():
   """ It supports CGI. It expects a configuration file with the following variables:
     sys_email=
     apikey=
     api_host=
     It supports Cross Origin Resource Sharing (CORS) by recognizing the HTTP "OPTIONS" REQUEST method.
     
   """
   os.environ["LANG"]="en_US.utf8"
   if len(sys.argv) < 2:
      sys.stderr.write("usage: config_file="+"\n")
      print_error("system failure: no configuration file.")
      return 1
   
   item_string=""
   doc_id=""
   item_id=""
   oclc=""
   oclc_number=""
   out_type="xml"
#######
########
   http_method=os.environ["REQUEST_METHOD"]
   
   form = cgi.FieldStorage()
   if len(form) == 0:
       print_error("Expected item_id, doc_id or oclc.")
       return 1
   if 'format' in form:
        out_type = form.getfirst("format")
   if 'item_id' in form:
        item_id = form.getfirst("item_id")
   elif 'doc_id' in form:
        doc_id = form.getfirst("doc_id")
   elif 'oclc' in form:
        print_error("oclc is not supported yet.")
        return 1
   else:
      print_error("Expected item_id, doc_id or oclc.")
      return 1
   #doc_id="990009263040302486"
   #doc_id="990022633760302486"
   #doc_id="990029398460302486" # federal register 2600+ items
   #out_type="marcedit"
   doc_id=doc_id.replace(" ","")
   item_id=item_id.replace(" ","")
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

   if doc_id <> "":
        try:
           doc_id=int(doc_id)
        except:
           print_error("doc_id must be a number")
           #sys.stderr.write("not a number\n")
           return 1
        try:
           alma_docid=str(doc_id)
           #sys.stderr.write(alma_docid+"\n")
# https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/"+str(mmsid)+"?apikey="+str(apikey),timeout=5)
           request_string="/almaws/v1/bibs/"+str(alma_docid)+"?apikey="+str(apikey)
           #sys.stderr.write(api_host+request_string+"\n")
           response,outcome=api_request(api_host,request_string)
           if outcome == 0:
               bib_string,outcome=get_bib_string(response)
               request_string="/almaws/v1/bibs/"+str(alma_docid)+"/holdings"+"?apikey="+str(apikey)
               #sys.stderr.write(request_string+" "+api_host+"\n")
               response,outcome=api_request(api_host,request_string)
               if outcome == 0:
                  holding_list,outcome=get_holding_list(response)
                  if outcome == 0:
                       for h_link in holding_list:
                           h_link+="/items?apikey="+str(apikey)+"&limit=100&offset=0"
                           url=h_link
                           outcome=0
                           if outcome == 0:
                              count=0
                              item_info=""
                              offset=0
                              item_info,offset,outcome=get_item_info(url,count,item_info,offset)
                              if outcome == 0:

                                 item_string+=item_info
                              else:
                                 sys.stderr.write("api request failed. get_item_info"+"\n")
                                 print_error("failed to get item stuff.")
                                 return 1

                           else:
                                 print_error("failed to get item stuff.")
                                 return 1
                       if out_type == "xml":
                            bib_string="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+"<collection xmlns=\"http://www.loc.gov/MARC21/slim\">"+bib_string+item_string+"</record></collection>"
                            print_result(bib_string,"xml")
                       else:
                            bib_string="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+"<collection>"+bib_string+item_string+"</record></collection>"
                            if out_type == "text":
                               print_result(bib_string,"text")
                            else:
                               print_result(bib_string,"marcedit")
                       return 0
                  else:
                       print_error("failed to get holding list")
                  return 0
               else:
                   print_error("failed to get holding record")
               return 0
           else:
               print_error("failed to get bib record..")
               return 1
        except:
           sys.stderr.write("api failed(1)\n")
           print_error("failed to get bib record.")
           return
        #print_result(doc_id)
   elif item_id <> "":
       request_string="/almaws/v1/items?item_barcode="+str(item_id)+"&apikey="+str(apikey)
       response,outcome=api_request(api_host,request_string)
       if outcome == 0:
          doc_id,outcome=get_docid(response)
          if outcome == 0:
           try:
              alma_docid=str(doc_id)
              request_string="/almaws/v1/bibs/"+str(alma_docid)+"?apikey="+str(apikey)
              response,outcome=api_request(api_host,request_string)
              if outcome == 0:
                  bib_string,outcome=get_bib_string(response)
                  request_string="/almaws/v1/bibs/"+str(alma_docid)+"/holdings"+"?apikey="+str(apikey)
                  response,outcome=api_request(api_host,request_string)
                  if outcome == 0:
                     holding_list,outcome=get_holding_list(response)
                     if outcome == 0:
                       for h_link in holding_list:
                           h_link+="/items?apikey="+str(apikey)+"&limit=100&offfset=0"
                           url=h_link
                           outcome=0
                           if outcome == 0:
                              count=0
                              item_info=""
                              offset=0
                              item_info,offset,outcome=get_item_info(url,count,item_info,offset)
                              if outcome == 0:

                                 item_string+=item_info
                              else:
                                 sys.stderr.write("api request failed. get_item_info"+"\n")
                                 print_error("failed to get item stuff.")
                                 return 1

                           else:
                                 print_error("failed to get item stuff.")
                                 return 1
                       if out_type == "xml":
                           bib_string="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+"<collection xmlns=\"http://www.loc.gov/MARC21/slim\">"+bib_string+item_string+"</record></collection>"
                           print_result(bib_string,"xml")
                       else:
                           bib_string="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+"<collection>"+bib_string+item_string+"</record></collection>"
                           if out_type == "text":
                               print_result(bib_string,"text")
                           else:
                               print_result(bib_string,"marcedit")
                       return 0
                  else:
                       print_error("failed to get holding list")
                       return 0
              else:
                   print_error("failed to get bib record;")
                   return 0
           except:
              sys.stderr.write("api failed(2)\n")
              print_error("failed to get bib record(1)")
              return 1
          else:
             print_error("failed to get bib id")
             return 1
       else:
          print_error("barcode failed")
          return 1
   elif oclc <> "":
     print_error("oclc not supported")
     return 0
   return 0


if __name__=="__main__":
  sys.exit(main())
  
