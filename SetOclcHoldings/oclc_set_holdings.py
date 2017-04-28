#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
   Program name: 
   Author: Bernardo Gomez
   Date: february, 2015
   Purpose:   
"""
import os
import sys 
import re
import signal
import hmac
import hashlib
import base64
import httplib
import time
import random

def main():
   if len(sys.argv) < 2:
      sys.stderr.write("usage: config_file="+"\n")
      return 1
   try:
      configuration=open(sys.argv[1],'r')
   except:
      sys.stderr.write("couldn't open config_file:"+sys.argv[1]+"\n")
      return 1

   clientId=""
   wskey=""
   principalID=""
   principal_namespace=""
   classification_scheme=""
   secret=""
   library_code="EMU"
   time_now=int(time.time())

   pat=re.compile("(.*?)=(.*)")
   for line in configuration:
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
     conn=httplib.HTTPSConnection("worldcat.org")
   except:
     sys.stderr.write("https failed\n")
     return 1

# HMAC signature:
#1.    The client’s WSKey
#2.    A timestamp value calculated for the request.
#3.    A nonce value generated for the request.
#4.    The request entity-body hash if one was calculated and included in the request, otherwise, an empty string.
#5.    The HTTP request method in upper case: HEAD, GET, POST, PUT, or DELETE
#6.    The string literal www.oclc.org
#7.    The string literal 443
#8.    The string literal /wskey
#9.    The query component of the web service request URI normalized

   try:
      for oclc_number in sys.stdin:
         try:
            conn=httplib.HTTPSConnection("worldcat.org")
         except:
            sys.stderr.write("https failed\n")
            return 1
         oclc_number=oclc_number.rstrip("\n")
         time_now=int(time.time())
# template:https://worldcat.org/ih/data?classificationScheme=LibraryOfCongress&instSymbol=&holdingLibraryCode=EMU&oclcNumber=2&cascade=1
         params="classificationScheme="+classification_scheme+"&instSymbol="+"&holdingLibraryCode="+library_code+"&oclcNumber="+oclc_number+"&cascade=1"
         query_components="cascade=1"+"\n"+"classificationScheme="+classification_scheme+"\n"+"holdingLibraryCode="+library_code+"\n"+"instSymbol="+"\n"+"oclcNumber="+oclc_number+"\n"
         nonce=str(random.randrange(1, 10000000))
         nonce=str(nonce)+str(time_now)
         try:
           message=wskey+"\n"+str(time_now)+"\n"+nonce+"\n"+""+"\n"+"POST"+"\n"+"www.oclc.org"+"\n"+"443"+"\n"+"/wskey"+"\n"+query_components
           sys.stderr.write(message+"\n")
           digest=hmac.new(secret, msg=message, digestmod=hashlib.sha256).digest()
           signature=base64.b64encode(digest) 
           sys.stderr.write(str(signature)+"\n")
         except:
            sys.stderr.write("hmac failed\n")
            continue
         value="http://www.worldcat.org/wskey/v2/hmac/v1 clientId=\""+str(clientId)+"\", timestamp=\""+str(time_now)+"\", nonce=\""+str(nonce)+"\", signature=\""+signature+"\", principalID=\""+principalID+"\", principalIDNS=\""+principal_namespace+"\""
         header={'Authorization': str(value)}
         sys.stderr.write(str(header)+"\n")
         try:
            conn.request("POST", "/ih/data?"+params,"",header)
         except:
            sys.stderr.write("http POST request failed\n")
            continue
         try: 
             response=conn.getresponse()
         except:
            sys.stderr.write("http get response  failed\n")
            continue
         try:
            sys.stdout.write(str(oclc_number)+"|"+str(response.status)+"|"+str(response.reason)+"|"+"\n")
            # success: oclc_number|200|OK|
         except:
            sys.stderr.write("couldn't display response\n")
            continue
         conn.close()
         #data=response.read()
         #print data
   except:
        pass
   return 0

if __name__=="__main__":
  sys.exit(main())
