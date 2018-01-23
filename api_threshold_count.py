#!/bin/python
import sys
import requests

def main():

  api_count = open("/sirsi/webserver/integrations/alma-api/alma_api_count.html", 'r')
  target = open("/sirsi/webserver/docs/alma_api_count.html", 'w')
  api_count = api_count.read()
  apikey = "[apikey]"
  url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/users"
  payload = {'limit': '10', 'apikey': apikey}
  r = requests.get(url, params=payload)
  headers = r.headers
  remaining_apis = headers['x-exl-api-remaining']
  api_count = api_count.replace('{api_count}', remaining_apis)
  target.write(api_count)

if __name__=="__main__":
  sys.exit(main())
