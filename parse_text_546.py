import sys
import re
r"""
Title: Parse text file for url
Author: Alex Cooper
Date: 06/08/2018
Purpose: Parse text file produced 
by marc_to_txt for 546
"""
#001||990032719490302486
#856|41|\puhttp://rstl.royalsocietypublishing.org/content/50.toc

def main():
  state = "init"
  rec_delim = "****"
  count = 0
  delim = "|"
  mmsid = ""
  title = ""
  lang = ""
  try:
    for line in sys.stdin:
      line = line.rstrip("\n")
      if state == "init":
        try:
          if line[0:4] == rec_delim:
            try:
              state = "new"
            except:
              sys.stderr.write("could not set state to new" + "\n")
        except:
          sys.stderr.write("could not find delimiter" + "\n")
      elif state == "new":
        if line[0:4] == "001|":
          mmsid = line[5: ]
        elif line[0:4] == "245|":
          title = re.search(r"\\pa(.*)", line)
          if title:
            title = title.group(1)
            title = re.sub("\\\p[a-z]", " ", title)
        elif line[0:4] == "546|":
          lang = line[7: ]
#          lang = re.sub("\\\p", " ", lang)
          lang = lang.split("\\p")
#          print len(lang)
          if len(lang) == 2:
            if lang[1][0] == "a":
              print mmsid + delim + title + delim + str(lang[1]).lstrip("a") + delim + "N/A"
            elif lang[1][0] == "b":
              print mmsid + delim + title + delim + "N/A" + delim + str(lang[1]).lstrip("b")
          elif len(lang) == 3:
            print mmsid + delim + title + delim + str(lang[1]).lstrip("a") + delim + str(lang[2]).lstrip("b")
  except:
    sys.stderr.write("could not parse lines" + "\n")

if __name__=="__main__":
  sys.exit(main())
