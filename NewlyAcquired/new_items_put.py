#!/opt/rh/python27/root/usr/bin/python
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus
import sys
import xml.etree.ElementTree as elementTree
import socks
import socket

#get bib
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
socket.socket = socks.socksocket
#get api key as program argument
#l7xx7ed1d73cf63d4105a2cf1df41632344f

def api_put(url,apikey,xml_string):

   queryParams = '?' + urlencode({ quote_plus('apikey') : apikey  })
   sys.stderr.write("params:"+queryParams+"\n")
   headers = {  'Content-Type':'application/xml'  }
   sys.stderr.write("put_url:"+url+"\n")
   request = Request(url + queryParams
    , data=xml_string
    , headers=headers)
   request.get_method = lambda: 'PUT'
   sys.stderr.write(str(request)+"\n")
   try:
      #response=urlopen(request,timeout=10)
      response=urlopen(request)
   except:
      sys.stderr.write("put failed"+"\n")
      return "",1
   response_code=response.getcode()
   sys.stderr.write("response_code:"+str(response_code)+"\n")
   if str(response_code) != "200":
      return "",1
   response_body = response.read()
   return response_body,0

def main():

  apiKey = sys.argv[1]

  for line in sys.stdin:
      try:
        mmsId = line.rstrip('\n')
#url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}'.replace('{mms_id}',quote_plus('990029398460302486'))
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}'.replace('{mms_id}',quote_plus(mmsId))
        queryParams = '?' + urlencode({ quote_plus('expand') : 'None' ,quote_plus('apikey') : apiKey })
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body_bib = urlopen(request).read()
#        print url
#        print response_body_bib
      except:
        sys.stderr.write("could not get marcxml "+mmsId+"\n")
#<datafield ind1=" " ind2=" " tag="598"><subfield code="a">NEW</subfield></datafield>
      try:
        tree = elementTree.fromstring(response_body_bib)
        child = elementTree.Element("datafield", ind1=" ", ind2=" ", my_crap="598")
        subfield = elementTree.SubElement(child, 'subfield', code="a")
        subfield.text = "NEW"
#### bernardo begin ##
        rec_tree = tree.find("record")
        rec_tree.append(child)
        xml_modified=elementTree.tostring(tree,encoding="utf-8",method="xml")
        xml_modified=xml_modified.replace("my_crap", "tag") 
        prolog="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        xml_modified=prolog+xml_modified
#### bernardo end ##
#        print xml_modified
      except:
        sys.stderr.write("could not update marcxml "+mmsId+"\n")
      try:
        response,outcome = api_put(url,apiKey,xml_modified)
### put also fails with original xml
###        response,outcome = api_put(url,apiKey,response_body_bib)
        if outcome == 0:
          sys.stderr.write("success"+"\n")
        else:
          sys.stderr.write("fatal error"+"\n")
      except:
        sys.stderr.write("PUT failed"+"\n")
      try:
        queryParams = '?' + urlencode({ quote_plus('apikey') : apiKey })
        values = xml_modified
        headers = {  'Content-Type':'application/xml'  }
        request = Request(url + queryParams
        , data = values
        , headers = headers)
        request.get_method = lambda: 'PUT'
        try:
            response_body = urlopen(request).read()
#            print response_body
        except:
            sys.stderr.write("could not call"+"\n")
      except:
        sys.stderr.write("could not execute PUT"+"\n")

if __name__=="__main__":
  sys.exit(main())
