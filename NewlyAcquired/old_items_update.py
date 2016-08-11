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
#l7xx2bea837c1e0a4ab68d5c23da8cee51ad

def api_put(url,apikey,xml_string):

   queryParams = '?' + urlencode({ quote_plus('apikey') : apikey  })
   sys.stderr.write("params:"+queryParams+"\n")
   headers = {  'Content-Type':'application/xml'  }
   sys.stderr.write("put_url:"+url+queryParams+xml_string+"\n")
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
      except:
        sys.stderr.write("could not get marcxml "+mmsId+"\n")
#<datafield ind1=" " ind2=" " tag="598"><subfield code="a">NEW</subfield></datafield>
      try:
        tree = elementTree.fromstring(response_body_bib)
      except:
        sys.stderr.write("could not parse response"+"\n")
      try:
        rec_tree = tree.find("record")
      except:
        sys.stderr.write("could not get record"+"\n")
      try:
        datafield = rec_tree.findall("datafield")
      except:
        sys.stderr.write("could not get datafields"+"\n")
      try:
        for df in datafield:
            try:
                tag = df.get("tag")
                try:
                    if tag == "598":
                        try:
                            subfield = df.findall("subfield")
                            for subf in subfield:
                                code = subf.get("code")
                                if code == "a":
                                    new = str(subf.text)
                                    if new == "NEW":
                                        rec_tree.remove(df)
                                        xml_modified=elementTree.tostring(tree,encoding="utf-8",method="xml")
                        except:
                            sys.stderr.write("could not parse subfield"+"\n")
                    else:
                        continue
                except:
                    sys.stderr.write("no 598"+"\n")
            except:
                sys.stderr.write("could not find 598"+"\n")
      except:
        sys.stderr.write("could not analyze datafields"+"\n")
      try:
        response,outcome = api_put(url,apiKey,xml_modified)
#        outcome = 0
#        print url
      except:
        sys.stderr.write("PUT failed 1111: "+url+"\n")
        continue
      if outcome == 0:
        sys.stderr.write("success"+"\n")
      else:
        sys.stderr.write("fatal error"+"\n")
        return 1

if __name__=="__main__":
  sys.exit(main())
