#!/bin/env python
# -*- coding: utf-8 -*-
"""
  webservice that receives a code belonging
  to a finding aid record, the name of a 
  Rose library repository; searches the code
  as a callnumber in Primo; and produces
  the barcodes of the ALMA items that
  match the callnumber.
  the output is an XML object.
"""
__author__ = 'bernardo gomez'
__date__ = 'september 2016'
__contributors__ = 'alex cooper, elizabeth roke'

import os
import sys
import re
import cgi
import cgitb; cgitb.enable(display=1, logdir="/tmp")
import time
import json
import requests
import xml.etree.ElementTree as elementTree

def get_copies(docid,repository,get_alma_record_url):
    """
       function queries ALMA via 
       custom webservice to get items associated
       with docid.
       items are listed in MARC "999" fields.
       function returns list of items, each
       containing two fields: 'barcode' and 
       callnumber 'description'.
    """
    copy_list=[]
    rose_location_list=['RSTORM','MSSTK']
    repository=repository.lower()
### fix finding aids typo next: spurious line-feed 
    repository=repository.replace("\n","")
    library=repository.split(" ")
    libr=[]
    if "robert" in library:
       libr="UNIV"
    elif "pitts" in library:
        libr="THEO"
    elif "rose" in library:
        libr="MARBL,LSC"
    elif "archives" in library:
        libr="MARBL,LSC"

    sys.stderr.write("libr:"+str(libr)+"\n")  
    #id="01EMORY_ALMA21156382500002486"  ## chinese 
    url=get_alma_record_url+str(docid)
    sys.stderr.write("get_alma_record:"+url+"\n")
    try:
          r=requests.get(url)
    except:
          sys.stderr.write("api request failed."+"\n")
    return_code=r.status_code
    if return_code == 200:
         response=r.content
    else:
        sys.stderr.write("FAILED(2)\n")
        response=r.content
        return copy_list,1
    #sys.stderr.write("return_code full record:"+str(return_code)+"\n")

    in_string=response.replace("\n","")
    in_string=in_string.replace(" xmlns=\"http://www.loc.gov/MARC21/slim\"","")
#collection xmlns="http://www.loc.gov/MARC21/slim"
    try:
         tree=elementTree.fromstring(in_string)
    except:
         sys.stderr.write("marcxml parse failed."+"\n")
         return copy_list,1
    try:
          record_element=tree.find("record")
    except:
          sys.stderr.write("xml parsing failed. couldn't find record element"+"\n")
          return copy_list,1
    try:
         datafield_element=record_element.findall("datafield")
    except:
         sys.stderr.write("xml parsing failed. couldn't find datafield"+"\n")
         return copy_list,1

    try:
         for dfield in datafield_element:
           tag_id=str(dfield.get("tag"))
           if tag_id == "999":
#              sys.stderr.write("tag 999\n")

               subfield=dfield.findall("subfield")
               field_text=""
               barcode="NONE"
               description="NONE"
               archive_item=False
               this_location=""
               this_libr=""
               for subf in subfield:
                    for k in subf.attrib.keys():
                       try:
                         if subf.get(k) == "a":
                            verify_callnum=str(subf.text)
                            verify_callnum=verify_callnum[0:3]
                            if str(verify_callnum) == "MSS" or str(verify_callnum) == "SER":
                                archive_item=True
                       except:
                          pass
                       try:
                         if subf.get(k) == "i":
                            barcode=str(subf.text)
                       except:
                          pass
                       try:
                         if subf.get(k) == "d":
                            description=str(subf.text)
                       except:
                          pass
                       try:
                         if subf.get(k) == "m":
                            this_libr=str(subf.text)
                            #sys.stderr.write("this_libr:"+this_libr+"\n")
                       except:
                          pass
                       try:
                         if subf.get(k) == "l":
                            this_location=str(subf.text)
                            #sys.stderr.write("this_libr:"+this_libr+"\n")
                       except:
                          pass
               if this_libr in libr:
                  if archive_item:
                       if this_location in rose_location_list:
                           copy_list.append(str(barcode)+"|"+str(description))
    #          sys.stderr.write("subfield "+str(barcode)+"|"+str(callnumber)+"\n")
    except:
         sys.stderr.write("xml parsing failed. datafield"+"\n")
    return copy_list,0

def get_alma_ids(pnx_record):
   """
      it parses primo pnx object to 
      get ALMA mms_ids of the 
      matched primo records.
      it returns a list of mms_ids.
   """
   alma_ids=[]

   try:
       tree=elementTree.fromstring(pnx_record)
   except:
       sys.stderr.write("pnx_record: fromstring failed"+"\n")
       return [],1
   try:
      lds17_node=tree.findall("display/lds17")
   except:
       sys.stderr.write("pnx_record: failed to get record_node"+"\n")
       return [],1

   sys.stderr.write("pnx_record: got record_node!"+"\n")
   for id in lds17_node:
       docid=str(id.text)
       alma_ids.append(docid)
   return alma_ids,0

def process_form(form, base_primo_url):
  """
     it extracts variables from the
     webform. 
     it queries Primo with callnumber.
     the query specifies that the 
     titles have "archives" as a 
     resource_type.
     it parses the primo HTML response
     to look for the primo IDs of the brief
     records that matched the query.
     function returns list if IDs.
  """
  object_id=str(form.getfirst("object_id"))
  repository=form.getfirst("repository")
  call_number=form.getfirst("call_number")
  docid_list=[]
  if call_number[0:8] == "Manuscri":
     this_callnumber="MSS"+object_id
  elif call_number[0:7] == "Series ":
     this_callnumber="SERIES"+object_id
  else:
     this_callnumber="UNDEFINED_STUFF"

  url=base_primo_url.replace("<CALLNUMBER>",this_callnumber)
  sys.stderr.write("pnx_url:"+url+"\n")
  try:
            r=requests.get(url)
  except:
            sys.stderr.write("api request failed."+"\n")
            return docid_list,1
  return_code=r.status_code
  if return_code == 200:
        response=r.content
  else:
        sys.stderr.write("FAILED(2)\n")
        response=r.content
        return docid_list,1
        #sys.stderr.write(str(response)+"\n")
  sys.stderr.write("return_code:"+str(return_code)+"\n")
  try:
     json_object=json.loads(response,encoding="utf-8")
  except:
      sys.stderr.write("json load is failing\n")
      return docid_list,1
  try:
      is_list=type(json_object["docs"]) is list
      if is_list:
         for doc in json_object["docs"]:
            mms_id=doc["addsrcrecordid"]
            if mms_id is None:
               sys.stderr.write("need more work\n")
            else:
               docid_list.append(str(mms_id))
  except:
      sys.stderr.write("json is failing\n")
      return [],1
  return docid_list,0

def print_result(copy_list):
  """
    it prints list of barcodes  in xml format.
  """
  print '%s' % "Content-Type: text/xml; charset=utf-8"
  print ""
  print '<?xml version="1.0"?>'
  print '<record>'
  for copy in copy_list:
     element=copy.split("|")
     print '<row>'
     print '<barcode>'+str(element[0])+'</barcode>'
     if str(element[1]) == "None":
         element[1]=""
     print '<description>'+str(element[1])+'</description>'
     print '</row>'
  print '</record>'
  return 0

def print_failure(description):
  """
    it prints an error message in xml.
  """
  print '%s' % "Content-Type: text/xml; charset=utf-8"
  print ""
  print '<?xml version="1.0"?>'
  print "<error_list>"
  print "<code>"+"ERROR"+"</code>"
  print "<description>"+description+"</description>"
  print "</error_list>"

  return

def quick_validation(form):
  """ 
     form has not variables: outcome=1. it should present form
     form is missing one or more variables: outcome > 100.
     for has all the variables: outcome = 0 .
  """

  fail=100
  if len(form) == 0:
      fail+=1
  if  'object_id' not in form:
      fail+=1
  if  'call_number' not in form:
      fail+=1
  if  'repository' not in form:
      fail+=1
  if fail > 100:
    return fail
  return 0



def main():
  """
    main function that expects a configuration file
    from the command line.
    configuration variables:
    base_primo_url=
    get_alma_record_url=

    it receives three HTTP variables:
       object_id ,
       call_number,
       repository.
  """
  if len(sys.argv)  < 2:
      print_failure("configuration file is missing")
      #send_email("produce_barcode_archives",sys_email,"[produce_barcode_archives] system failure", no_config_file)
      return 1

  try:
        configuration=open(sys.argv[1], 'rU')
  except IOError:
        print_failure("configuration file is missing")
        #send_email("produce_barcode_archives",sys_email,"[produce_barcode_archives] system failure open config",sys.argv[1] )
        return 1
  sys_email="bgomez@emory.edu"
  base_primo_url=""
  get_alma_record_url=""

  pat=re.compile("(.*?)=(.*)")
  for line in configuration:
      m=pat.match(line)
      if m:
         if m.group(1) == "sys_email":
              sys_email=m.group(2)
         if m.group(1) == "base_primo_url":
              base_primo_url=m.group(2)
         if m.group(1) == "get_alma_record_url":
              get_alma_record_url=m.group(2)
  fail=0
  if sys_email== "":
     host=socket.gethostbyaddr(socket.gethostname())
     hostname=host[0]
     sys_email="alma"+"@"+hostname
  if base_primo_url == "":
     fail+=1
  if get_alma_record_url == "":
     fail+=1
  if fail > 0:
    print_failure("incomplete web service configuration")
    return 1


  os.environ["LANG"]="en_US.utf8"
  alma_docid_list=[]
  form = cgi.FieldStorage()
  outcome=quick_validation(form)
  repository=form.getfirst("repository")
  copy_list=[]
  if outcome == 0:
    primoid_list,outcome=process_form(form, base_primo_url)
    if outcome == 0:
        for id in primoid_list:
              copies,outcome=get_copies(id,repository,get_alma_record_url)
              if outcome == 0:
                 sys.stderr.write(str(copies)+"\n")
                 copy_list=copy_list+copies
        if len(copy_list) > 0:
              print_result(copy_list)
        else:
              print_failure("no repository copies found.")
    else:
        print_failure("no alma ids found!")
        return 0
#    print_failure("primo ids:"+str(primoid_list)+" almaids:"+str(alma_docid_list))
  else:
    print_failure("missing parameters. expected: object_id, call_number, repository")
  return 0


if __name__ == "__main__":
  sys.exit(main())

