#!/bin/env python
# -*- coding: utf-8 -*-
r"""
   Author: Alex Cooper & Bernardo Gomez
   Date: August, 2016
   Purpose: get oclc ids of deleted/withdrawn alma records
"""
import os
import sys
import random
import re
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
def get_item_info(rows,id_list):
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
    url = "https://na03.alma.exlibrisgroup.com/view/sru/[institutionId]?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma."
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
       if m.group(1) == "types":
          types=m.group(2)

  configuration.close()

  in_string=""
  outcome=1
  payload={'apikey':apikey,'path':path,'limit':limit}
  sys.stderr.write("analytics path:"+str(path)+"\n")
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
  sys.stderr.write("finished:"+str(finished.text)+"\n")
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
          result_node=tree.findall("QueryResult/ResultXml/rowset/Row")
      except:
          sys.stderr.write("couldn't find rowset."+"\n")
          return outcome
      #sys.stderr.write("result_node:"+str(result_node)+"\n")
      if len(result_node) == 0:
         sys.stderr.write("empty result. exiting.."+"\n")
         return 1
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
           result_node=tree.findall("QueryResult/ResultXml/rowset/Row")
#           print result_node
         except:
            sys.stderr.write("couldn't find rowset."+"\n")
            return outcome
         if len(result_node) == 0:
            sys.stderr.write("empty result"+"\n")
            return 1
         id_list,outcome=get_item_info(result_node,id_list)
  else:
         try:
           result_node=tree.findall("QueryResult/ResultXml/rowset/Row")
         except:
            sys.stderr.write("couldn't find rowset."+"\n")
            return outcome
         if len(result_node) == 0:
            sys.stderr.write("empty result"+"\n")
            return 1
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
         if types == "deleted":
             if no_records == str(0):
#                 print str(id.split("|")[0])
                 oclc_row = str(id.split("|")[0])
                 oclc_id.append(oclc_row)
             else:
                 oclc_row = str(id.split("|")[1])
                 sys.stderr.write(oclc_row + " exists in Alma" + "\n")
         elif types == "withdrawn":
             if no_records == str(1):
#                 print str(id.split("|")[0])
                 oclc_row = str(id.split("|")[0])
                 oclc_id.append(oclc_row)
             elif no_records > str(1):
                 oclc_row = str(id.split("|")[1])
                 sys.stderr.write(oclc_row + " can be found in more than one record in Alma" + "\n")
  for ids in oclc_id:
      print str(ids)
  return 0

if __name__=="__main__":
  sys.exit(main())
