#!/opt/rh/python27/root/usr/bin/python
r"""
Title: Meyer SFTP File Backup
Author: Alex Cooper
Date: 01/25/2018
Purpose: Retrieve data backup once a week
"""
import sys
import pysftp
import re

def main():

  #######################################
  # Open and process configuration file #
  #######################################
  try:
    configs = open("/alma/config/meyer_sftp.cfg")
  except:
    sys.stderr.write("could not find configuration file" + "\n")
  pat = re.compile("(.*?)=(.*)")
  for line in configs:
    line = line.rstrip("\n")
    m = pat.match(line)
    if m:
      if m.group(1) == "remote_dir":
        remote_dir = m.group(2)
      elif m.group(1) == "local_dir":
        local_dir = m.group(2)
      elif m.group(1) == "server":
        server = m.group(2)
      elif m.group(1) == "un":
        un = m.group(2)
      elif m.group(1) == "pwd":
        pwd = m.group(2)

  #####################################
  # Make sftp call and retrieve files #
  #####################################
  with pysftp.Connection(server, username=un, password=pwd) as sftp:
    sftp.get_d(remote_dir, local_dir)

  ##########################################
  # Uncomment this line to print variables #
  ##########################################
#  print remote_dir + "	" + local_dir + "	" + server + "	" + un + "	" + pwd

if __name__=="__main__":
  sys.exit(main())
