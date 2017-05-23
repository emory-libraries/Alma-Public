#!/bin/env python
# -*- coding: utf-8 -*-
r"""
   Author: Alex Cooper
   Date: May, 2017
   Purpose: get oclc ids of deleted alma ebook records
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
from collections import OrderedDict
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

####get the oclc numbers from the xml
def get_item_info(rows,id_list):
   ocolc = re.compile("^\(OCoLC\)\d")
   ocn = re.compile("^ocn\d")
   ocm = re.compile("^ocm\d")
   oclc_no="N/A"
   net_no = "N/A"
   for this_row in rows:
      item_row=""
      try:
          this_node=this_row.find("Column1")
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
          sys.stderr.write("couldn't find Column8."+"\n")
#          return id_list,outcome
#      item_row=str(bib_cycle + "|" + mod_date + "|" + mmsId + "|" + net_no + "|" + oclc_no + "|" + material_type + "|" + title)
#      print net_no
      item_row = str(oclc_no)
      id_list.append(item_row)
   return id_list,0

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
  socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
  socket.socket = socks.socksocket
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
        
         socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
         socket.socket = socks.socksocket
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
  for ids in id_list:
      if ids != "N/A":
          sys.stdout.write(ids + "\n")
      else:
          continue

if __name__=="__main__":
  sys.exit(main())
