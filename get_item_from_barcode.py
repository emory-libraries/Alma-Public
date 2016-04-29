#!/opt/rh/python27/root/usr/bin/python
'''
Title: get_item_links
Purpose: get item links from a list of barcodes
Author: Alex C.
Date: 12/21/2015
'''

import sys
import re
import os
import xml.etree.ElementTree as elementTree

from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

####get item information
####https://api-na.hosted.exlibrisgroup.com/almaws/v1/items?item_barcode=010001389333&apikey=[apiKey]

#to type in a barcode
#barcode = raw_input('Enter a barcode: ')

#to hardcode the barcode
#barcode = str('010001389333')

#to feed in a barcode
#barcode = str(sys.stdin.read()).strip('\n')

#input for api key as program argument
apiKey = sys.argv[1]

#to use a file of barcodes as input
for line in sys.stdin:
    try:
        barcode = line.strip('\n')
    except:
        sys.stderr.write('could not take barcode'+'\n')
#print barcode

#get item information
url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/items'
queryParams = '?' + urlencode({ quote_plus('item_barcode') : barcode ,quote_plus('apikey') : apiKey })
request = Request(url + queryParams)
print url + queryParams
request.get_method = lambda: 'GET'
item_body = urlopen(request).read()
#print item_body
target = open('/tmp/output2.xml', 'w')
target.write(str(item_body))
target.close()
tree = elementTree.fromstring(item_body)
url = tree.get('link')
#print url

#update item 
tree = elementTree.parse('/tmp/output2.xml')
root = tree.getroot()
for itemNote in root.iter('internal_note_3'):
    itemNote.text = str('good bye')
tree.write('/tmp/updated.xml')
my_file = open('/tmp/updated.xml')
file_contents = my_file.read()

#url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings/{holding_id}/items/{item_pid}'.replace('{mms_id}',quote_plus('990022126200302486')).replace('{holding_id}',quote_plus('22230794840002486')).replace('{item_pid}',quote_plus('23230794830002486'))
queryParams = '?' + urlencode({ quote_plus('apikey') : apiKey  })
values = file_contents
headers = {  'Content-Type':'application/xml'  }
request = Request(url + queryParams
, data=values
, headers=headers)
request.get_method = lambda: 'PUT'
response_body = urlopen(request).read()
#print response_body

sys.exit()
