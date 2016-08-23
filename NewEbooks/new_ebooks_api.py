#!/opt/rh/python27/root/usr/bin/python
# -*- coding: utf-8 -*-
r"""
   Program name: parse_new_ids.py
   Author: Bernardo Gomez/Alex Cooper
   Date: june, 2016
   Purpose:   
"""
import os
import sys 
import re
import requests
import xml.etree.ElementTree as elementTree


def get_item_info(result_node,id_list):
   outcome=1
   try:
          rows=result_node.findall("Row")
   except:
          sys.stderr.write("couldn't find Rows."+"\n")
          return id_list,outcome
   mms_id=""
   item_creation=""
   item_modification=""
   item_status=""
   timestamp=""
   process_type=""
   receiving_date=""
   barcode=""
   holding_id=""
   item_id=""
   for this_row in rows:
      item_row=""
      try:
          this_node=this_row.find("Column1")
          mms_id=str(this_node.text)
      except:
          sys.stderr.write("couldn't find Column1."+"\n")
          return id_list,outcome
      try:
          this_node=this_row.find("Column2")
          active_date=str(this_node.text)
      except:
          sys.stderr.write("couldn't find Column2."+"\n")
          return id_list,outcome
      item_row=str(mms_id)
      id_list.append(item_row)
   return id_list,0

def get_record_ids(result_node,id_list):
   outcome=1
   try:
          rows=result_node.findall("Row")
   except:
          sys.stderr.write("couldn't find Rows."+"\n")
          return id_list,outcome
   for this_row in rows:
      try:
          id_node=this_row.find("Column3")
          id_list.append(str(id_node.text))
      except:
          sys.stderr.write("couldn't find Column3."+"\n")
          return id_list,outcome
   return id_list,0


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
  for id in id_list:
     print str(id)
  return 0

if __name__=="__main__":
  sys.exit(main())
