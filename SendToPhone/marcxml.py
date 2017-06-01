#!/bin/env python
# -*- coding: utf-8 -*-

r"""
  biblio class processes MARCXML string.
  
"""
__author__ = "bernardo gomez"
__date__ = " march 2017"
import os
import sys
import re
import xml.etree.ElementTree as elementTree

class biblio:
  """
     init function receives a MARCXML string.   
  """
  def __init__(self,in_string):
     """
       it receives a MARCXML string.
       it converts MARCXML into a MARC text format.
       record delimiter is "*****"
       leader is "000" field.
       subfield delimiter is "\p"
       example:
       ******
       000|  |02222cam a2200433Ka 4500
       001|  |990031707790302486
       005|  |20160112000551.0
       008|  |111005s2012    enk           000 0 eng d
       020|  |\pa1906548633 (pbk.)
       (...)
       100|1 |\paAbad Faciolince, Héctor Joaquín.
       240|10|\paTratado de culinaria para mujeres tristes.\plEnglish
       (...)
       
       biblio stores MARC text in a list of strings.
     """
     self.lines=[]
     delimiter="|"
     data=in_string.replace("\n","")
     m=re.search(r".*<collection.*?>.*<record.*?>(.*)",data)
     if m:
       data=m.group(1)
       data="<collection><record>"+data
       try:
           tree=elementTree.fromstring(data)
       except:
           sys.stderr.write("marcxml: fromstring failed"+"\n")
           raise Exception
       try:
           record = tree.find("record")
       except:
           sys.stderr.write("xml parsing failed"+"\n")
           raise Exception
       space=" "
       try:
           leader=record.find("leader").text
           self.lines.append("******")
           temp="000|  |"+leader
           self.lines.append("000|  |"+leader)
           #print "leader:"+leader
       except:
           sys.stderr.write("marcxml parsing: didn't find leader"+"\n")
           raise Exception
       try:
           controlfields=record.findall("controlfield")
       except:
           sys.stderr.write("marcxml parsing: didn't find controlfields"+"\n")
           raise Exception
       try:
         for cfield in controlfields:
           attribute=cfield.attrib
           value=str(cfield.text)
           value=value.replace(" ","^")
           temp=attribute['tag']+"|  |"+value
           self.lines.append(attribute['tag']+"|  |"+value)
       except:
           sys.stderr.write("xml parsing failed. defective controlfield"+"\n")
           raise Exception
        
       try:
          datafield_element=record.findall("datafield")
       except:
           sys.stderr.write("xml parsing failed. couldn't find datafield"+"\n")
           raise Exception
       try:
           for dfield in datafield_element:
                try:
                   field_info=str(dfield.get("tag"))+"|"+str(dfield.get("ind1"))+str(dfield.get("ind2"))+"|"
                except:
                    sys.stderr.write("xml parsing failed. couldn't build field_info"+"\n")
                    raise Exception
                try:
                    subfield=dfield.findall("subfield")
                except:
                    sys.stderr.write("xml parsing failed. couldn't find subfields.."+"\n")
                    raise Exception
                field_text=""
                for subf in subfield:
                    for k in subf.attrib.keys():
                       try:
                         #if subf.get(k) != "0":
                            #field_text=field_text+"$$"
                            field_text=field_text+"\\p"
                            field_text=field_text+subf.get(k)
                            subfield_text=subf.text
                            try:
                               if subfield_text is None:
                                  subfield_text=""    
                               field_text=field_text+subfield_text
                               if field_text.isdigit():     
                                      field_text=str(field_text)
                            except:
                                sys.stderr.write("passing:"+str(subfield_text)+"\n")
                                pass
                       except:
                          sys.stderr.write("error in subfield\n")
                          raise Exception
                self.lines.append(field_info+field_text)
       except:
          sys.stderr.write("xml parsing failed. couldn't find subfield"+"\n")

       return

  def get_field(self,tag):
     """
        it retrieves string corresponding to "tag". 
        it returns a list of fields for the given tag.
     """
     self.field=[]
     for line in self.lines:
        if line[0:3] == tag:
           self.field.append(line)

     return self.field
