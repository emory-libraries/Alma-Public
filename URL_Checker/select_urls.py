#!/bin/env python
# -*- coding: utf-8 -*-
"""
   it reads BIB records from standard input represented in text format 
   and it writes text lines compatible with the URL checker
   program.
   an input record looks like:
   ******
   001||990032719490302486
   856|10|\puhttp://http://vendorsite.com

   the corresponding output line looks like:
   http://vendorsite.com_|_990032719490302486_|_1_|_

"""
__author__='bernardo gomez'
__date__='january 2008'

import os
import sys
import re
import time

def main():
 pat_newrec=re.compile(r"\*{5}")
 state="INIT"
 f_001=""
 tab="	"
 delimiter="_|_"
 try:
   for line in sys.stdin:
      line=line.rstrip("\n")
      m_newrec=pat_newrec.match(line)
      if m_newrec:
        if state == "INIT":
          f_856=[]
          f_001=""
          state="READING"
        else:
           if f_001 != "":
              for entry in f_856:
                 print entry+delimter+f_001+delimiter+"Bibliographic"+delimiter
              f_856=[]
              f_001=""
      else:
           m_f001=re.match(r"001\|\|(.*)",line)
           if m_f001:
             f_001=m_f001.group(1)
             continue
           m_f856=re.match(r"856\|(..)\|(.*)",line)
           if m_f856:
              if m_f856.group(1)[0:1] != "4" and m_f856.group(1)[0:1] != "7":
                  if m_f856.group(1)[0:1] == " " and m_f856.group(1)[1:2] == " ":
                     continue
                  sys.stderr.write("invalid 856 field:"+tab+f_001+tab+line+tab+"\n")
                  continue
              s_f856=re.search(r"\\pu(.*?)\\p",line)
              if s_f856:
                f_856.append(s_f856.group(1))
              else:
                s_f856=re.search(r"\\pu(.*)",line)
                if s_f856:
                    f_856.append(s_f856.group(1))
              continue
           continue
 except:
       return 0
 if state != "INIT" and f_001 != "":
     for entry in f_856:
          print entry+delimiter+f_001+delimiter+"Bibliographic"+delimiter
 return 0


if __name__ == "__main__":
  sys.exit(main())


