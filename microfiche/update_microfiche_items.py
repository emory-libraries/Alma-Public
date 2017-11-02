#!/bin/python
r"""
Author: Alex Cooper
Title: Update microfiche items
Purpose: Add number of fiche to the item
record from the 533 in the bib record
Date: 11/02/2017
"""
import sys
import requests
import re
import json
import xml.etree.ElementTree as ET

# mmsId: 9936668100502486
# barcode: EMU170703
def get_bib_record(mmsid,apikey,url):
  """
  API call to get bib record xml
  """
  outcome = 1
  response = header = ""
  try:
    payload = {'apikey': apikey, 'mms_id': mmsid}
    r = requests.get(url, params=payload)
    status = r.status_code
    if status == 200:
      response = r.content
      header = r.headers
      outcome = 0
    else:
      sys.stderr.write("get bib record failed" + "\n")
      return outcome,"N/A","N/A"
  except:
    sys.stderr.write("get bib record failed" + "\n")
  return outcome,response,header

def parse_bib_record(tree):
  """
  Parse the bib record xml to
  get number of fiche from 533
  """
  outcome = 1
  try:
    datafields = tree.findall("bib/record/datafield")
    for d in datafields:
      tag = d.get("tag")
      if tag == "533":
        subfields = d.findall("subfield")
        for sf in subfields:
          code = sf.get("code")
          if code == "e":
            item_info = sf.text
  except:
    sys.stderr.write("could not parse xml" + "\n")
    return "N/A",outcome
  return item_info,outcome

def main():
  """
  Get configuration items and run 
  through the functions
  """
  try:
    configuration = open("/sirsi/webserver/config/alma_microfiche_updates.cfg", "rU")
  except:
    sys.stderr.write("could not open configuration file" + "\n")
  try:
    pat = re.compile("(.*?)=(.*)")
    for line in configuration:
      line = line.rstrip("\n")
      m = pat.match(line)
      if m:
        if m.group(1) == "apikey":
          apikey = m.group(2)
        elif m.group(1) == "url":
          url = m.group(2)
        elif m.group(1) == "anal_apikey":
          anal_apikey = m.group(2)
        elif m.group(1) == "anal_url":
          anal_url = m.group(2)
        elif m.group(1) == "path":
          path = m.group(2)
  except:
    sys.stderr.write("could not parse configuration file" + "\n")
  configuration.close()
  for line in sys.stdin:
    mmsid = line.rstrip("\n")
    mmsid = str(mmsid)
    outcome,response,header = get_bib_record(mmsid,apikey,url)
    if outcome == 0:
      tree = ET.fromstring(response)
      item_info,outcome = parse_bib_record(tree)
      print item_info
      nos_of_apis_left = header['x-exl-api-remaining']
    else:
      sys.stderr.write("get bib api call failed" + "\n")

if __name__=="__main__":
  sys.exit(main())
