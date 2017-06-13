#!/bin/env python
# -*- coding: utf-8 -*-
"""
  this webservice searches ISBNs on Primo
  to assert whether they exist at emory
   libraries.
  it presents a webform with three fields:
     secretword;
     file with ISBNs; and
     email address that receives results. 
"""
__author__ = 'bernardo gomez'
__date__ = 'july 2016'

import os
import sys
import re
import cgi
import time
import json
import socket
import subprocess
import requests
import xml.etree.ElementTree as elementTree
import cgitb; cgitb.enable(display=1, logdir="/tmp")


def verify_ip():
  """
    not used. it allows HTTP requests from all IP addresses.
  """
## allow all geographical location, for the time being

  return 0
##
  ip_addr=os.getenv('REMOTE_ADDR')
  if ip_addr:
    ip_number=ip_addr.split('.')#10.110.
    if ip_number[0]!="170" or ip_number[1]!="140" or ip_number[0]!="10" or ip_number[1] != "110":
       return 1
  return 0

def create_log_entry(log_file,target_file,network_id, file_size):
   """
     it creates an entry on a log file. not used.
   """
   timestamp=time.strftime('%Y%m%d%H%M%S',time.localtime())
   log_entry=timestamp+"|"+target_file+"|"+file_size+"|"+network_id+"|"+"\n"
   try:
      log_file.write(log_entry)
   except:
      sys.stderr.write("search_isbn\n")
   return

def print_form(file_name,message):
  """
     it sends the html page stored in
     'file_name'along with the 
     message to standard output.
  """
  try:
     file=open(file_name, 'rU')
  except:
     file_name=""
  if file_name == "":
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    print "<html>"
    print "<head><title>Error message</title></head>"
    print "<body>"
    print "<h2>"+message+"</h2>"
    print "</body>"
    print "</html>"
  else:
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    for line in file:
        line=line.replace(r"<!--MESSAGE=-->",message)
        print line,
    file.close()
  return


def get_record_info(url):
   """
     this function queries primo
     via the PNX API service.
     it parses the json response
     to extract the first ALMA
     mms_id and the title.
     it returns the mms_id
     and the title.
   """
   pid=""
   title=""
   outcome=1
   try:
      r=requests.get(url)
   except:
      sys.stderr.write("http request failed:"+url+"\n")
      return "","",1
   return_code=r.status_code
   sys.stderr.write("return_code:"+str(return_code)+"\n")
   if str(return_code) == "200":
     response=r.content
   else:
     sys.stderr.write("get_record failed:"+str(r.content)+"\n")
     return "","",1
   try:
       json_object=json.loads(response,encoding="utf-8")
   except:
       sys.stderr.write("json load is failing\n")
       return "","",1
   try:
      is_list=type(json_object["docs"]) is list
      if is_list:
         if len(json_object["docs"]) == 0:
            return "","",0
         for doc in json_object["docs"]:
            pid=doc["pnxId"]
            if pid is None:
               sys.stderr.write("need more work\n")
            else:
               pid=str(pid)
               title=doc["title"]
               try:
                  ## turn a number into a character string.
                  int(title)
                  title=str(title)
               except:
                    pass
               break
   except:
      sys.stderr.write("json is failing\n")
      return "","",1

   return pid,title,0


def process_form(form_file, max_file_size,result_file,source_file,url,mail_list,permalink_base,mail_script):
  """
     this function receives all the fields 
     from the web form 
     and additional variables to perform the 
     the search against PRIMO.
     the webform supplies a text file
     with ISBNs to search.
     if the ISBN has one or more matches, then
     the function builds a permalink to
     the first match.
     if the ISBN doesn't have a match, then
     the function builds a deep link to worldcat.
     the function send the list of searches to 
     the specified mailboxes.
  """
  workf_prefix="/tmp/process_spinomatic_"
  pid=str(os.getpid())
  workfile=workf_prefix+pid
  delim="\t"
  sys.stderr.write("form_file:"+str(form_file)+"\n")
  sys.stderr.write("work_file:"+str(workfile)+"\n")
  sys.stderr.write("result_file:"+str(result_file)+"\n")
  if source_file.file:
    in_string=source_file.file.read()
    source_file.file.close()
 

  try:
       result=open(result_file,'w')
  except:
      print_failure(form_file,"ERROR: couldn't open result file.")
      return
  lines=in_string.split("\n")
  sys.stderr.write(str(lines)+"\n")
  #result.write("barcode"+delim+"outcome"+delim+"description"+delim+"recommendation"+delim+"\n")
  list=[]
  excel_buster="' "
  result.write("isbn"+delim+"match"+delim+"title"+delim+"permalink"+delim+"\n")
  for isbn in lines:
      isbn=isbn.rstrip("\n")
      isbn=isbn.rstrip("\r")
      try:
          if isbn <> "":
            int(isbn)
      except:
          result.write(excel_buster+str(isbn)+delim+"ERROR"+delim+"isbn is not an integer"+""+delim+"\n")
          continue
      if str(isbn)  <> "":
         api_url=url.replace("<ISBN>",str(isbn))
         #sys.stderr.write(url+"\n")
         pid,title,outcome=get_record_info(api_url)
         if outcome == 0:
#http://discovere.emory.edu/discovere:default_scope:01EMORY_ALMA21233511590002486
            if pid != "":
              permalink=permalink_base+str(pid)
              result.write(excel_buster+str(isbn)+delim+"YES"+delim+title[0:80]+delim+permalink+delim+"\n")
            else:
              result.write(excel_buster+str(isbn)+delim+"NO"+delim+""+delim+"http://worldcat.org/isbn/"+str(isbn)+delim+"\n")
  result.close()
  #####os.unlink(workfile)
  if os.path.exists(result_file):

       command=mail_script+" "+result_file+" "+mail_list
       sys.stderr.write("command:"+command+"\n")

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
          print_failure(form_file,"Success:text file will go to your mailbox.")
          return 0
       else:
          sys.stderr.write("ERROR\n")
          print_failure(form_file,"ERROR: file conversion failed. input file might not be MARC.")
          return 1
  else:
       print_failure(form_file,"ERROR: searches failed.")
       return 1

  return

def print_failure(file_name, message):
 """
  it prints an html page with an error message.
 """
 try:
     file=open(file_name, 'rU')
 except:
     file_name=""
 if file_name == "":
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    print "<html>"
    print "<head><title>Error message</title></head>"
    print "<body>"
    print "<h2>"+message+"</h2>"
    print "</body>"
    print "</html>"
 else:
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    for line in file:
        line=line.replace(r"<!--MESSAGE=-->",message)
        print line,
    file.close()
 return


def send_email(prog_name,email_list,subject,message):
  """
     it sends an email message via python smtp library.
  """
  import smtplib
  import socket

  from email.MIMEText import MIMEText
  host=socket.gethostbyaddr(socket.gethostname())
  hostname=host[0]
  msg = MIMEText(message)
  COMMASPACE = ', '
  address=email_list.split(',')
  if len(address) > 1:
     msg['To'] = COMMASPACE.join(address)
  else:
     msg['To'] = email_list
  msg['Subject'] = subject
  host=socket.gethostbyaddr(socket.gethostname())
  hostname=host[0]
  sender="sirsi"+"@"+hostname
  msg['From'] = sender

# Establish an SMTP object and connect to your mail server
  s = smtplib.SMTP()
# s.connect("smtp.service.emory.edu")
  s.connect("localhost")
# Send the email - real from, real to, extra headers and content ...
  s.sendmail(sender,address, msg.as_string())

  return

def quick_validation(form):
  """ 
     it receives a CGI form 
     and validates the fields.
     form  has no variables: outcome=1. action: it should present form
  """

  fail=100
  if len(form) == 0:
      return 1
  if  'secretword' not in form:
      fail+=1
  if  'source' not in form:
      fail+=1
  if fail > 100:
    return fail
  return 0


def main():
  """
    webservice that expects a configuration file from 
    the command line.
    configuration variables:
       directory
       file_prefix
       form_file
       max_file_size
       secretword
       permalink_base
       pnx_url
       sys_email
       mail_script
   
    it presents a webform to HTTP client.
    webform variables:
        secretword ( it acts a password);
        text file with isbns;
        email address(es) that will receive 
        search result.
    it sends email message via a shell script
     ( search_isbn.sh )
  """
  host=socket.gethostbyaddr(socket.gethostname())
  hostname=host[0]

  sys_email="webserver"+"@"+hostname
  sys.stderr.write("sys_email:"+sys_email+"\n")
  if len(sys.argv)  < 2:
      print_failure("","Internal system failure. configuration file is missing.")
      return 1

  try:
        configuration=open(sys.argv[1], 'rU')
  except IOError:
        print_failure("","Internal system failure(1).")
        send_email("search_isbn",sys_email,"[search_isbn] system failure open config",sys.argv[1] )
        return 1
  sys_email="bgomez@emory.edu"
  form_file=""
  secretword=""
  max_file_size=""
  log_file_name=""
  directory=""
  file_prefix=""
  apikey=""
  permalink_base=""
  pnx_url=""
  mail_script=""

  pat=re.compile("(.*?)=(.*)")
  for line in configuration:
      m=pat.match(line)
      if m.group(1) == "sys_email":
              sys_email=m.group(2)
      if m.group(1) == "form_file":
              form_file=m.group(2)
      if m.group(1) == "secretword":
              secretword=m.group(2)
      if m.group(1) == "max_file_size":
              max_file_size=m.group(2)
      if m.group(1) == "log_file_name":
              log_file_name=m.group(2)
      if m.group(1) == "directory":
              directory=m.group(2)
      if m.group(1) == "file_prefix":
              file_prefix=m.group(2)
      if m.group(1) == "permalink_base":
              permalink_base=m.group(2)
      if m.group(1) == "pnx_url":
              pnx_url=m.group(2)
      if m.group(1) == "mail_script":
              mail_script=m.group(2)

  fail=0
  if sys_email== "":
     host=socket.gethostbyaddr(socket.gethostname())
     hostname=host[0]
     sys_email="alma"+"@"+hostname
  if directory == "":
     send_email("search_isbn",sys_email,"[search_isbn] config. file didn't define directory",sys.argv[1] )
     fail+=1
  if file_prefix == "":
     send_email("search_isbn",sys_email,"[search_isbn] config. file didn't define file_prefix",sys.argv[1] )
     fail+=1
  if form_file == "":
     send_email("search_isbn",sys_email,"[search_isbn] config. file didn't define form_file",sys.argv[1] )
     fail+=1
  if pnx_url == "":
     send_email("search_isbn",sys_email,"[search_isbn] config. file didn't define pnx_url",sys.argv[1] )
     fail+=1
  if secretword == "":
     send_email("search_isbn",sys_email,"[search_isbn] config. file didn't define secretword",sys.argv[1] )
     fail+=1
  if mail_script == "":
     send_email("search_isbn",sys_email,"[search_isbn] config. file didn't define mail_script",sys.argv[1] )
     fail+=1
  if max_file_size  == "":
     send_email("search_isbn",sys_email,"[search_isbn] config. file didn't define max_file_size",sys.argv[1] )
     fail+=1
  #if log_file_name == "":
     #send_email("search_isbn",sys_email,"[search_isbn] config. file didn't define log_file_name",sys.argv[1] )
     #fail+=1
  
  if fail > 0:
    print_failure("","Internal system failure(2).")
    return 1

  try:
    test_file=open(form_file,'rU')
    test_file.close()
  except:
    print_failure("","Internal system failure(3).")
    send_email("search_isbn",sys_email,"[search_isbn] can't open form file",sys.argv[1] )
    return 1


  os.environ["LANG"]="en_US.utf8"

  form = cgi.FieldStorage()
  outcome=quick_validation(form)
  pid=str(os.getpid())
  today_is=time.strftime('%Y%m%d',time.localtime())
  result_file=directory+"/"+file_prefix+today_is+"_"+pid+".xls"
  #sys.stderr.write("result_file:"+result_file+"\n")
  if outcome == 0:
    password=form.getfirst('secretword')
    if password != secretword:
       print_failure(form_file,"Secret word doesn't match")
       return 1
    source_file=form["source"]
    mail_list=form.getfirst("email")
    mail_list=re.sub(" +",",",mail_list)
    mail_list=mail_list.rstrip(",")


    process_form(form_file,max_file_size,result_file,source_file,pnx_url,mail_list,permalink_base,mail_script)
  #log_file.close()

  if outcome == 1:
    print_form(form_file,"")
    return

  if outcome > 100:
    print_form(form_file,"expected fields are missing.")
  return


if __name__ == "__main__":
  sys.exit(main())
  
