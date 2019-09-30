#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  This program contains "worldcat_identities_link" function 
  that retrieves the BIBFRAME object for a given ALMA MMS_ID
  and extracts the Library of Congress Control Number of the corresponding
  personal name used as the main entry in the bibliographic record.
  In other words, worldcat_identities_link() parses the 
  bibframe XML and looks for the "library of congress control number"
  assigned to the work's author ("PrimaryContribution").

"""
__author__ = "bernardo gomez"
__date__ = " september 2019"

import os
import sys 
import re
import requests
import xml.etree.ElementTree as elementTree

def worldcat_identities_link(doc_id,linked_data_host):
   """
     Parameters: 
       -  doc_id, ALMA's mms_id 
       -  linked_data_host, EXLIBRIS server that receives
          the BIBFRAME API request
     This function receives the BIBFRAME XML object; it parses
     the XML object to extract the the library of congress control
     number corresponding to the "Main contributor"
     
     It returns the worldcat_identity link
     
     Note that the worldcat indentity base URL is hard-coded
     https://worldcat.org/identities/lccn-
   """

   link=""
   outcome=1

   worldcat_uri="https://worldcat.org/identities/lccn-"

   url=linked_data_host+str(doc_id)
   try:
      r=requests.get(url, timeout=10)
   except:
      sys.stderr.write("HTTP get failed\n")
      return link,outcome
   status=r.status_code
   if status == 200:
       response=r.content
   else:
       return link,outcome

   in_string=response.replace("\n","")
   try:
       tree=elementTree.fromstring(in_string)
   except:
      return link,outcome

   if tree is None:
       return link,outcome

   work_element=tree.find('{http://id.loc.gov/ontologies/bibframe/}Work') 
   if work_element is None:
       return link,outcome

   contribution_element=work_element.findall('{http://id.loc.gov/ontologies/bibframe/}contribution')
   if len(contribution_element) == 0:
       return link,outcome

   primary_contributor=False

   for contribution in contribution_element:
     Contribution=contribution.find('{http://id.loc.gov/ontologies/bibframe/}Contribution')
     if Contribution is None:
       return link,outcome

     for child in Contribution:
       if child.tag == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type':
           if child.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'] == 'http://id.loc.gov/ontologies/bflc/PrimaryContribution':
              primary_contributor=True
       if child.tag == '{http://id.loc.gov/ontologies/bibframe/}agent':
            author_element=child.find('{http://id.loc.gov/ontologies/bibframe/}Agent')
            if author_element is None:
                  return link,outcome
            authority_uri=author_element.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about']
     if primary_contributor is True:
          name_id=re.compile("http://id.loc.gov/authorities/names/(.*)")
          m=name_id.match(authority_uri)
          if m:
             lccn=m.group(1)
             link=worldcat_uri+str(lccn)
             return  link,0
   return link,0


def main():
   """ 
      It calls worldcat_identities_link()
      linked_data_host = https://open-na.hosted.exlibrisgroup.com/alma/01GALI_EMORY/bf/entity/instance/
      Note: plug in your own mms_id in 
      docid_list=["990020275880302486"]
   """
   os.environ["LANG"]="en_US.utf8"

   docid_list=["990020275880302486"]
   #docid_list=["990029881400302486"]
   #docid_list=["9936709901402486"]
   linked_data_host="https://open-na.hosted.exlibrisgroup.com/alma/01GALI_EMORY/bf/entity/instance/"
   identities_link,outcome=worldcat_identities_link(str(docid_list[0]),linked_data_host)
   print  identities_link
   return 0

if __name__=="__main__":
  sys.exit(main())
