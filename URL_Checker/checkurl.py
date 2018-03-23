#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   checkurl.py reads from standard input a text file that contains URLs; it performs an HTTP
   GET to test the URL and it writes the result to standard output.
   input line format: URL_|_record_id_|_resource_type
   output line format: HTTP/1.1_|_return_code_|_response description_|_text_|_input_line
"""
import requests
import sys
import os
import re
import argparse
import socket
import socks
import subprocess

def http_request(url,my_timeout,line,response_file):
      """
    it performs an HTTP GET request  and sends a formatted response to 
    standard output. it invokes curl to perform the HTTP request.
    curl response codes:
       1      Unsupported protocol. This build of curl has no support for this protocol.
       2      Failed to initialize.
       3      URL malformed. The syntax was not correct.
       5      Couldn’t resolve proxy. The given proxy host could not be resolved.
       6      Couldn’t resolve host. The given remote host was not resolved.
       7      Failed to connect to host.
       8      FTP weird server reply. The server sent data curl couldn’t parse.
       9      FTP  access denied. The server denied login or denied access to the particu-
              lar resource or directory you wanted to  reach.  Most  often  you  tried  to
              change to a directory that doesn’t exist on the server.
       11     FTP  weird  PASS  reply.  Curl  couldn’t  parse  the  reply sent to the PASS
              request.
       13     FTP weird PASV reply, Curl  couldn’t  parse  the  reply  sent  to  the  PASV
              request.
       14     FTP weird 227 format. Curl couldn’t parse the 227-line the server sent.
       15     FTP can’t get host. Couldn’t resolve the host IP we got in the 227-line.
       17     FTP couldn’t set binary. Couldn’t change transfer method to binary.
       18     Partial file. Only a part of the file was transferred.
       19     FTP  couldn’t  download/access the given file, the RETR (or similar) command
              failed.
       28     Operation  timeout.  The  specified time-out period was reached according to
              the conditions.
      """
###  ugly hack to allow HTTPS requests out of turing.
      socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
      socket.socket = socks.socksocket
###
      this_hostname=re.compile(r"(http://|https://)(.*?)(/|\?)")
      short_url=re.compile(r"(http://|https://)(.*)")
      hnm=this_hostname.match(url)
      if hnm:
         hostname=hnm.group(2)
      else:
         shortname=short_url.match(url)
         if shortname:
            hostname=shortname.group(2)
      command="echo "+"'"+url+"'"+" | curl_to_checkurl.sh -t "+str(my_timeout)+" -h "+hostname+" -w "+response_file

      try:
         #p=subprocess.Popen(command, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
         p=subprocess.Popen(command, shell=True,stdout=subprocess.PIPE,stderr=None)
      except:
         sys.stderr.write("subprocess failed"+"\n")
         print_failure(form_file,"ERROR: failed to run subprocess.")
         return 1
      try:
          p.wait()
      except:
          sys.stderr.write("subprocess wait failed"+"\n")
          print_failure(form_file,"ERROR: failed to run subprocess.")
          return 1
#  (mods_string,error_string)=p.communicate()
      if p.returncode == 0:
         http_response=re.compile(r"(HTTP/1.\d )(\d\d\d)(.*)")
         http_redirect=re.compile(r"(Location: )(.*)")
         try:
             response_f=open(response_file,'Ur')
         except:
             sys.stdout.write("HTTP/1.1_|_610_|_failed to open response file_|__|_"+line+"\n")
             return
         location=""
         description=""
         for r_line in response_f:
             r_line=r_line.strip("\r")
             r_line=r_line.strip("\n")
             rcode=http_response.match(r_line)
             if rcode:
                http_code=int(rcode.group(2))
                description=rcode.group(3)
             redirect=http_redirect.match(r_line)
             if redirect:
                location=redirect.group(2)
         if http_code == 301 or http_code == 302 or http_code == 307 or http_code == 308:
             sys.stdout.write("HTTP/1.1_|_"+str(http_code)+"_|_"+location+"_|__|_"+line+"\n")
         else:
             sys.stdout.write("HTTP/1.1_|_"+str(http_code)+"_|_"+str(description)+"_|__|_"+line+"\n")
      elif p.returncode == 6:
          sys.stdout.write("HTTP/1.1_|_603_|_unknown hostname_|__|_"+line+"\n")
      elif p.returncode == 28:
          sys.stdout.write("HTTP/1.1_|_605_|_connection timed out_|__|_"+line+"\n")
      else:
          sys.stdout.write("HTTP/1.1_|_607_|_connection failed. curl code:"+str(p.returcode)+"_|__|_"+line+"\n")
      response_f.close()
      os.unlink(response_file)
      return 

def test_pid(url,timeout,line,response_file):
    """
      it queries http://pid.emory.edu/xxxx to extract the target URL and it
      invokes http_request() to perform the check.
    """

###  ugly hack to allow HTTPS requests out of turing.
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
    socket.socket = socks.socksocket
###
    hostname="pid.emory.edu"
    location=""
    command="echo "+"'"+url+"'"+" | curl_to_checkurl.sh -t "+str(timeout)+" -h "+hostname+" -w "+response_file

    try:
         p=subprocess.Popen(command, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except:
         sys.stderr.write("subprocess failed"+"\n")
         print_failure(form_file,"ERROR: failed to run subprocess.")
         return 1
    try:
          p.wait()
    except:
          sys.stderr.write("subprocess wait failed"+"\n")
          print_failure(form_file,"ERROR: failed to run subprocess.")
          return 1
#  (mods_string,error_string)=p.communicate()
    if p.returncode == 0:
         http_response=re.compile(r"(HTTP/1.\d )(\d\d\d)(.*)")
         http_redirect=re.compile(r"(Location: )(.*)")
         ezproxy=re.compile(r"(http://|https://)(proxy.library.emory.edu/login\?url=?)(.*)")
         http_code=int(200)
         redirection=None
         try:
             response_f=open(response_file,'Ur')
         except:
             sys.stdout.write("HTTP/1.1_|_610_|_failed to open response file_|__|_"+line+"\n")
             return
         for r_line in response_f:
             r_line=r_line.strip("\r")
             r_line=r_line.strip("\n")
             rcode=http_response.match(r_line)
             if rcode:
                http_code=int(rcode.group(2))
             
             redirection=http_redirect.match(r_line)
             if redirection:
                   location=redirection.group(2)
         if http_code == 301 or http_code == 302 or http_code == 307 or http_code == 308:
            mezp=ezproxy.match(location)
            if mezp: 
                location=mezp.group(3)
            http_request(location,timeout,line,response_file)
          
    else:
          sys.stdout.write("HTTP/1.1_|_607_|_connection failed. curl code:"+str(p.returcode)+"_|__|_"+line+"\n")
    response_f.close()
    os.unlink(response_file)
    return 

def main():
   """
      this script uses requests module to perform a GET. it receives  optional arguments:
        --timeout the default timeout value is 10 seconds.
        --exclude file . "file" contains hostnames whose URLs should be ignored.
        --workdir . "directory" contains the directory where curl will deposit the HTTP response.

      "requests" module is not as granular with return codes as "curl", but curl would have to be
      embedded in a bash script. bash regular regex processor is GREEDY, whereas python's regex is more
      powerful.
      this script has an optimization: if the previous URL has been checked it ignores the current URL.
   """
   parser=argparse.ArgumentParser(description='it checks URLs contained in text file')
   parser.add_argument('--timeout',"-t", dest='timeout', type=int,nargs=1, help="timeout value in seconds")
   parser.add_argument('--exclude',"-e", dest='exclude', nargs=1, help="exclusion file")
   parser.add_argument('--workdir',"-w", dest='workdir', nargs=1, required=True, help="work directory")
   args = parser.parse_args()
   try:
       my_timeout=args.timeout[0]
   except:
       my_timeout=int(10)

   workdir=args.workdir[0]
   try:
       exclude_file=args.exclude[0]
   except:
       exclude_file=""

   exclude_list=[]
   if exclude_file <> "":
     try:
        exclude_f=open(exclude_file,'rU')
        for row in exclude_f:
            row=row.rstrip("\n")
            exclude_list.append(row)
     except:
         exclude_list=[]

   process_id=str(os.getpid())
   response_file=workdir+"response_"+process_id
   try:
      this_hostname=re.compile(r"(http://|https://)(.*?)(/|\?)")
      short_url=re.compile(r"(http://|https://)(.*)")
      ezproxy=re.compile(r"(http://|https://)(proxy.library.emory.edu/login\?url=?)(.*)")
      persistent_id=re.compile(r"(http://|https://)(pid.emory.edu/)(.*)")
      previous_url="===="
      for line in sys.stdin:
          line=line.rstrip("\n")
          if line == "URL_|_ID_|_Resource Type":
             continue
          try:
             (url,key,resource_type)=line.split("_|_")
          except:
              sys.stderr.write("invalid line. it should be url_|_record_id_|_resource_type\n")
              continue
          if previous_url == url:
             continue
          previous_url=url
          m=this_hostname.match(url)
          if m:
                hostname=m.group(2)
          else:
             mu=short_url.match(url)
             if mu:
                hostname=mu.group(2)
             else:
                sys.stdout.write("HTTP/1.1_|_606_|_Not an HTTP URL_|__|_"+line+"\n");
                continue
          if hostname in exclude_list:
              continue
          pidm=persistent_id.match(url)
          if pidm:
              test_pid(url,my_timeout,line,response_file)
              continue
          mp=ezproxy.match(url)
          if mp:
             url=mp.group(3)
          http_request(url,my_timeout,line,response_file)
   except:
       pass
   return 0

if __name__ == "__main__":
  sys.exit(main())
