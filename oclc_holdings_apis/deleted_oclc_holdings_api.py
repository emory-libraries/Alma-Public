#!/opt/rh/python27/root/usr/bin/python
# -*- coding: utf-8 -*-
r"""
   Author: Alex Cooper/Bernardo Gomez
   Date: August, 2016
   Purpose: delete oclc holdings
"""
import os
import sys
import random
import re
import socks
import socket
import requests
import xml.etree.ElementTree as elementTree
import datetime as dt
import signal
import hmac
import hashlib
import base64
import httplib
import time
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

####get the oclc numbers from the xml
def get_item_info(result_node,id_list):
   outcome=1
   try:
          rows=result_node.findall("Row")
   except:
          sys.stderr.write("couldn't find Rows."+"\n")
          return id_list,outcome
   ocolc = re.compile("^\(OCoLC\)\d")
   ocn = re.compile("^ocn\d")
   ocm = re.compile("^ocm\d")
   oclc_no="N/A"
   bib_cycle="N/A"
   mmsId="N/A"
   net_no="N/A"
   material_type="N/A"
   mod_date="N/A"
   title="N/A"
   for this_row in rows:
      item_row=""
      try:
          this_node=this_row.find("Column7")
          net_no=str(this_node.text)
          try:
              if ocm.match(net_no):
                  oclc_no = net_no.strip( 'ocm' )
              elif ocn.match(net_no):
                  oclc_no = net_no.strip( 'ocn' )
              elif ocolc.match(net_no):
                  oclc_no = net_no.strip( '(OCoLC)' )
              else:
                  oclc_no = "N/A"
          except:
              sys.stderr.write("could not parse oclc number" + "\n")
      except:
          sys.stderr.write("couldn't find Column7."+"\n")
#          return id_list,outcome
#      item_row=str(bib_cycle + "|" + mod_date + "|" + mmsId + "|" + net_no + "|" + oclc_no + "|" + material_type + "|" + title)
      item_row=str(oclc_no) + "|" + str(net_no)
      id_list.append(item_row)
   return id_list,0

####ensure there is no record with that oclc number still in Alma
def check_oclc_numbers(id,query):
    outcome = 1
    id_check = "okay"
    url = "https://na03.alma.exlibrisgroup.com/view/sru/01GALI_EMORY?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma."
    oclc_no = id.split("|")
    oclc_no = oclc_no[1]
    oclc_no = str(oclc_no)
    queryParams = urlencode({ query : oclc_no })
    try:
        request = Request(url + queryParams)
        result = urlopen(request).read()
    except:
        sys.stderr.write("no oclc no" + "\n")
    return result,0

####delete oclc holdings via worldcat
def delete_oclc_holdings(ids,config):
   outcome = 1
   try:
#      print "opening config"
      configuration=open(config,'Ur')
   except:
      sys.stderr.write("couldn't open config_file:"+sys.argv[1]+"\n")
      return 1

   clientId=""
   wskey=""
   principalID=""
   principal_namespace=""
   classification_scheme=""
   institution_id=""
   secret=""
   library_code="EMU"
   time_now=int(time.time())

   pat=re.compile("(.*?)=(.*)")
   for line in configuration:
#      print "reading config"
      line=line.rstrip("\n")
      m=pat.match(line)
      if m:
         if m.group(1) == "clientId":
              clientId=m.group(2)
              wskey=clientId
         if m.group(1) == "principalID":
              principalID=m.group(2)
         if m.group(1) == "principal_namespace":
              principal_namespace=m.group(2)
         if m.group(1) == "classification_scheme":
              classification_scheme=m.group(2)
         if m.group(1) == "institution_id":
              institution_id=m.group(2)
         if m.group(1) == "secret":
              secret=m.group(2)
         if m.group(1) == "library_code":
              library_code=m.group(2)
#         print clientId+"|"+principalID+"|"+principal_namespace+"|"+classification_scheme+"|"+institution_id+"|"+secret+"|"+library_code
# clientId is the same as WSKEY
   fail=0
   if clientId == "":
      sys.stderr.write("clientId is missing in config. file"+"\n")
      fail+=1
   if principalID == "":
      sys.stderr.write("principalID is missing in config. file"+"\n")
      fail+=1
   if principal_namespace == "":
      sys.stderr.write("principal_namespace is missing in config. file"+"\n")
      fail+=1
   if classification_scheme == "":
      sys.stderr.write("classification_scheme is missing in config. file"+"\n")
      fail+=1
   if secret == "":
      sys.stderr.write("oclc secret is missing in config. file"+"\n")
      fail+=1
   if institution_id == "":
      sys.stderr.write("institution_id is missing in config. file"+"\n")
      fail+=1
   if fail > 0:
      return 1
   try:
#     print "trying to connect"
     conn=httplib.HTTPSConnection("worldcat.org")
   except:
     sys.stderr.write("https failed\n")
     return 1
   oclc_number=ids
   time_now=int(time.time())
   params="classificationScheme="+str(classification_scheme)+"&holdingLibraryCode="+str(library_code)+"&oclcNumber="+str(oclc_number)+"&cascade=1"
   query_components="cascade=1"+"\n"+"classificationScheme="+str(classification_scheme)+"\n"+"holdingLibraryCode="+str(library_code)+"\n"+"oclcNumber="+str(oclc_number)+"\n"
   nonce=str(random.randrange(1, 10000000))
   nonce=str(nonce)+str(time_now)
   try:
###    create HMAC signature
       message=wskey+"\n"+str(time_now)+"\n"+nonce+"\n"+""+"\n"+"DELETE"+"\n"+"www.oclc.org"+"\n"+"443"+"\n"+"/wskey"+"\n"+query_components
       sys.stderr.write(message+"\n")
       digest=hmac.new(secret, msg=message, digestmod=hashlib.sha256).digest()
       signature=base64.b64encode(digest) 
       sys.stderr.write(str(signature)+"\n")
   except:
       sys.stderr.write("hmac failed\n")
   value="http://www.worldcat.org/wskey/v2/hmac/v1 clientId=\""+str(clientId)+"\", timestamp=\""+str(time_now)+"\", nonce=\""+str(nonce)+"\", signature=\""+signature+"\", principalID=\""+principalID+"\", principalIDNS=\""+principal_namespace+"\""
   header={'Authorization': str(value)}
   sys.stderr.write(str(header)+"\n")
   try:
       conn.request("DELETE", "/ih/data?"+params,"",header)
   except:
       sys.stderr.write("http DELETE request failed\n")
   try: 
       response=conn.getresponse()
   except:
       sys.stderr.write("http get response  failed\n")
   try:
       sys.stdout.write(str(oclc_number)+"|"+str(response.status)+"|"+str(response.reason)+"|"+"\n")
   except:
       sys.stderr.write("couldn't display response\n")
   conn.close()
         #data=response.read()
         #print data
   return 0

####get reults of deleted records from analytics
def main():

  if len(sys.argv) < 2:
     sys.stderr.write("system failure. configuration file is missing."+"\n")
     return 1

  try:
     configuration=open(sys.argv[1], 'Ur')
  except:
     sys.stderr.write("couldn't open configuration file "+sys.argv[1]+"\n")
     return 1

  pat=re.compile("(.*?)=(.*)")
  for line in configuration:
    line=line.rstrip("\n")
    m=pat.match(line)
    if m:
       if m.group(1) == "url":
          url=m.group(2)
       if m.group(1) == "path":
          path=m.group(2)
       if m.group(1) == "apikey":
          apikey=m.group(2)
       if m.group(1) == "limit":
          limit=m.group(2)

  configuration.close()

  in_string=""
  outcome=1
  payload={'apikey':apikey,'path':path,'limit':limit}
  try:
     r=requests.get(url,params=payload)
  except:
     sys.stderr.write("api request failed."+"\n")
     return [],outcome
  return_code=r.status_code
  if return_code == 200:
     response=r.content
#     print response
  else:
     sys.stderr.write("FAILED(1)\n")
     response=r.content
     sys.stderr.write(str(response)+"\n")
     return 1
  in_string=response
  in_string=in_string.replace("\n","")
  in_string=in_string.replace(" xmlns=\"urn:schemas-microsoft-com:xml-analysis:rowset\"","")
  try:
      tree=elementTree.fromstring(in_string)
  except:
      sys.stderr.write("parse failed(1)."+"\n")
      return outcome
  try:
       finished=tree.find("QueryResult/IsFinished")
  except:
      sys.stderr.write("parse failed(2)."+"\n")
      return outcome
  id_list=[]
  if finished.text == "false":
      try:
         token=tree.find("QueryResult/ResumptionToken")
      except:
         sys.stderr.write("parse failed(3)."+"\n")
         return outcome
      this_token=str(token.text)
      id_list=[]
      sys.stderr.write(str(url)+" "+str(apikey)+" "+this_token+" "+str(id_list)+" "+limit+"\n")
      try:
          result_node=tree.find("QueryResult/ResultXml/rowset")
      except:
          sys.stderr.write("couldn't find rowset."+"\n")
          return outcome
      id_list,outcome=get_item_info(result_node,id_list)
      work_to_do=True
      outcome=1
      while work_to_do:
        
         payload={'apikey':apikey,'token':this_token,'limit':limit}
         try:
            r=requests.get(url,params=payload)
         except:
            sys.stderr.write("api request failed."+"\n")
            return outcome
         return_code=r.status_code
         if return_code == 200:
            response=r.content
         else:
            sys.stderr.write("FAILED(2)\n")
            response=r.content
            sys.stderr.write(str(response)+"\n")
            return outcome
         in_string=response
         in_string=in_string.replace("\n","")
         in_string=in_string.replace(" xmlns=\"urn:schemas-microsoft-com:xml-analysis:rowset\"","")
         try:
              tree=elementTree.fromstring(in_string)
         except:
              sys.stderr.write("parse failed(1)."+"\n")
              return outcome
         try:
              finished=tree.find("QueryResult/IsFinished")
         except:
             sys.stderr.write("parse failed(2)."+"\n")
             return outcome
         if finished.text == "true":
             work_to_do=False
         try:
           result_node=tree.find("QueryResult/ResultXml/rowset")
#           print result_node
         except:
            sys.stderr.write("couldn't find rowset."+"\n")
            return outcome
         id_list,outcome=get_item_info(result_node,id_list)
  else:
         try:
           result_node=tree.find("QueryResult/ResultXml/rowset")
         except:
            sys.stderr.write("couldn't find rowset."+"\n")
            return outcome
         id_list,outcome=get_item_info(result_node,id_list)
  oclc_id = []
  for id in id_list:
     oclc_no = str(id.split("|")[1])
     if oclc_no != "No OCLC Number Available":
         id_check,outcome = check_oclc_numbers(id,"other_system_number")
         id_check=id_check.replace("record xmlns=\"\"","record")
         id_check=id_check.replace(" xmlns=\"http://www.loc.gov/zing/srw/\"","")
         id_check=id_check.replace("\n","")
         tree=elementTree.fromstring(id_check)
         check_result = tree.find("numberOfRecords")
         no_records = check_result.text
         if no_records == str(0):
#             print str(id.split("|")[0])
             oclc_row = str(id.split("|")[0])
             oclc_id.append(oclc_row)
         else:
             oclc_row = str(id.split("|")[1])
             sys.stderr.write(oclc_row + " exists in Alma" + "\n")
  for ids in oclc_id:
#      print ids
      config = "/alma/config/delete_oclc_holdings.cfg"
      outcome = delete_oclc_holdings(ids,config)
  return 0

if __name__=="__main__":
  sys.exit(main())
