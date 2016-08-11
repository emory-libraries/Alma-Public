#!/opt/rh/python27/root/usr/bin/python
#Author: Alex
#Purpose: check pending file against current Alma items
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus
import sys
import xml.etree.ElementTree as elementTree
import socks
import socket

#get bib
from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus
#l7xx7ed1d73cf63d4105a2cf1df41632344f
#990036464790302486|22318733790002486|23318733770002486|

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
socket.socket = socks.socksocket

#mms_id = "9936572720402486"
#holding_id = "22319416980002486"
#item_id = "23319416960002486"
api_key = sys.argv[1]

for line in sys.stdin:
    try:
        data = line.split('|')
        mms_id = data[0]
        holding_id = data[1]
        item_id = data[2]
    except:
        sys.stderr.write("could not parse data"+"\n")
#get record
    try:
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings/{holding_id}/items/{item_id}'.replace('{mms_id}',quote_plus(mms_id)).replace('{holding_id}',quote_plus(holding_id)).replace('{item_id}',quote_plus(item_id))
        queryParams = '?' + urlencode({ quote_plus('limit') : '10' ,quote_plus('offset') : '0' ,quote_plus('apikey') : api_key  })
        request = Request(url + queryParams)
        request.get_method = lambda: 'GET'
        response_body = urlopen(request).read()
#        print response_body
    except:
        sys.stderr.write("api call failed"+"\n")
#analyse items
    try:
        tree = elementTree.fromstring(response_body)
    except:
        sys.stderr.write("could not parse response"+"\n")
    try:
        item_data = tree.findall('item_data/process_type')
    except:
        sys.stdout.write("could not get item info"+"\n")
    for item in item_data:
        try:
            process_type = str(item.text)
#            print process_type
	    if process_type == "None":
                sys.stdout.write(mms_id+"\n")
	    elif process_type == "LOAN":
                sys.stdout.write(mms_id+"\n")
	    elif process_type == "HOLDSHELF":
                sys.stdout.write(mms_id+"\n")
        except:
            sys.stderr.write("could not get process type"+"\n")

sys.exit(0)
