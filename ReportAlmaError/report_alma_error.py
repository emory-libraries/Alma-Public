#!/bin/env python
# -*- coding: utf-8 -*-
r"""
   webservice that receives one or more ALMA mms_ids
   and presents a webform to send 
   a  note about the bibliographic record to a specified 
   email address.
"""
__author__ = 'bernardo gomez'
__date__ = 'august 2016'

import os
import sys 
import cgi
import re
import requests
from datetime import date, datetime
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(email_list,subject,message,smtp_server):

  """
     it sends email address to specified mail list via
     smtp_server as defined in configuration file.
  """
  import smtplib
  from email.MIMEText import MIMEText
  msg = MIMEText(message)
  COMMASPACE = ', '
  address=email_list.split(',')
  if len(address) > 1:
     msg['To'] = COMMASPACE.join(address)
  else:
     msg['To'] = email_list
  msg['Subject'] = subject
  ############
  #
  sender="do-not-reply"+"@"+"yourhostname.library.emory.edu"
  ##########
  msg['From'] = sender

# Establish an SMTP object and connect to your mail server
  s = smtplib.SMTP(smtp_server)
  s.sendmail(sender,address, msg.as_string())
  s.quit()
  return


def verify_record(url,doc_id):
   """
     it invokes custom webservice to get
     bibliographic record. it verifies
     doc_id (alma mms_id).
     it returns success=0 if mms_id is found;
     it returns failure=1 if record or mms_id
     doesn't exist.
   """
   outcome=1
   request_url=url+str(doc_id)+"&format=text"
   try:
      r=requests.get(request_url, timeout=10)
   except:
      sys.stderr.write("api request failed. \n")
      return outcome
   status=r.status_code
   if status == 200:
       bib_string=r.content
   else:
       return outcome

   bib_string=bib_string.replace("\n","")
   field_001=re.compile(".*(001\|\|\d+?).*")
   m=field_001.match(bib_string)
   if m:
      outcome=0
   else:
      outcome=1
   return outcome

def say_hello_to_bot():
   """
     it displays html page with message
     to web robots.
   """
   time.sleep(5)

   print '%s' % "Content-Type: text/html; charset=utf-8"
   print ""
   print "<!DOCTYPE html>"
   print "<html>"
   print "<head>"
   print "<title>report problem</title>"
   print "</head>"
   print "<body>"
   print "<h2>Thank you!</h2>"
   print "</body>"
   print "</html>"
   return


def process_form(form,email_list,doc_id,reply_to,smtp_server):
   """
      it reads webform variables and sends email message,
      if bibliographic record exists.
   """
   if 'comment' in form:
      comment=form.getfirst('comment')
   else:
      comment="NO COMMENT"
   note=""
   if 'state' in form:
      state=form.getfirst('state')
      if state == '2':
        note="Note:"+str(doc_id)+" "+"doesn't exist"+"\n"
      else:
        if reply_to == "":
           note="mms_id:"+str(doc_id)+"\n"
        else:
           note="mms_id:"+str(doc_id)+"\n"+"reply_to: "+str(reply_to)+"\n"
   comment=note+comment
   try:
      send_email(email_list,"primo error report",comment,smtp_server)
   except:
      sys.stderr.write("email failure\n")

   print '%s' % "Content-Type: text/html; charset=utf-8"
   print ""
   print "<!DOCTYPE html>"
   print "<html>"
   print "<head>"
   print "<title>report problem</title>"
   print "</head>"
   print "<body>"
   print "<h2>Thank you for your report or comment.</h2>"
   print "</body>"
   print "</html>"
   return

def  print_form(input_page,doc_id,state):
   """
      it builds html page based on template
      contained in input_page file.
   """
   print '%s' % "Content-Type: text/html; charset=utf-8"
   print ""
   time_stamp=time.time()
   time_stamp=int(time_stamp)
   time_stamp=str(time_stamp)

   try:
      webform=open(input_page,'Ur') 
   except:
      display_html_failure("system failure. couldn't open input form")
      return
   for line in webform:
        line=line.replace(r"<!--SESSION=-->",time_stamp);
        line=line.replace(r"<!--ALMA_ID=-->",doc_id);
        line=line.replace(r"<!--STATE=-->",state);
        print line
   return

def display_html_failure(message):
   """
     it prints an html page with a message when
     there is a fatal failure.
   """
   print '%s' % "Content-Type: text/html; charset=utf-8"
   print ""

   print "<!DOCTYPE html>"
   print "<html lang=\"en-US\">"
   print "<head>"

   print "<title>Failure</title>"
   print  "<style>a.menu_xml_http{font-weight:bold;}</style>"
   print  "<meta charset=\"utf-8\">"
   print  "<meta name=\"viewport\" content=\"width=device-width\">"
   print   "<meta name=\"Keywords\" content=\"\">"
   print   "<meta name=\"Description\" content=\"\">"
   print   "<link rel=\"icon\" href=\"/favicon.ico\" type=\"image/x-icon\">"

   print  "<style type=\"text/css\">"

   print  "</style>"


   print "</head>"

   print "<body>"
   print  "<hr>"
   print  "<p>"
   print  message
   print "<p>"


   print "</body>"
   print  "</html>"
   return 0



def main():
   """
      this CGI script receives an http request with  list of ALMA mms_ids 
      and it presents a web form with two fields:
      comment and email_address.
      the email address is optional.
      the script verifies the first mms_id against ALMA.
      the script emails the comment and the user's email address to
      the mailbox designated in the configuration file.
   """
   if len(sys.argv) < 2:
      sys.stderr.write("usage: config_file="+"\n")
      display_html_failure("System failure. no configuration file.")
      return 1

   doc_id=""
   input_page=""
   get_record_url=""
   email_list=""
   smtp_server=""
   try:
     configuration=open(sys.argv[1],"Ur")
   except:
      display_html_failure("System failure. couldn't open configuration file.")
      return 1


   pat=re.compile("(.*?)=(.*)")
   for line in configuration:
      m=pat.match(line)
      if m:
         if m.group(1) == "input_page":
              input_page=m.group(2)
         if m.group(1) == "sys_email":
              sys_email=m.group(2)
         if m.group(1) == "email_list":
              email_list=m.group(2)
         if m.group(1) == "smtp_server":
              smtp_server=m.group(2)
         if m.group(1) == "get_record_url":
             get_record_url=m.group(2)


   if input_page  == "":
      display_html_failure("System failure. input file.")
   if get_record_url  == "":
      display_html_failure("System failure. no get_record_url")
      return 1
   if smtp_server  == "":
      display_html_failure("System failure. no smtp_server.")
      return 1

   try:
      inputf=open(input_page,"Ur")
   except:
      display_html_failure("System failure. couldn't open form page.")
      return 1

   form = cgi.FieldStorage()

   if len(form) == 0:
       display_html_failure("unable to process request: doc_id is missing.")
       return 1

   if  'doc_id' not in form:
      display_html_failure("unable to process request: doc_id is missing")
      return 1
   try:
       docids=form.getfirst('doc_id')
   except:
      display_html_failure("unable to get doc_id.")
      return 1
   if 'email2' in form:
      email2=form.getfirst('email2')
      if email2 != "":
         say_hello_to_bot()
         return
   if 'session' in form:
       time_stamp=form.getfirst('session')
       try:
          time_stamp=int(time_stamp)
       except:
          time_stamp=0
       time_now=time.time()
       time_now=int(time_now)
       if time_now - time_stamp >0 and time_now - time_stamp < 2:
           say_hello_to_bot()
           return
       
   state=""
   if 'state' in form:
       state=form.getfirst('state')

   if 'email' in form:
      reply_to=form.getfirst('email')

   if state == "":
       docid_list=docids.split(",")
       outcome=verify_record(get_record_url,str(docid_list[0]))
       record_OK=False
       if outcome == 0:
           record_OK=True

       if record_OK:
          print_form(input_page,str(docids),"1")
       else:
          print_form(input_page,str(docids),"2")
   else:
          http_method=os.environ["REQUEST_METHOD"]
          if http_method == "POST":
             process_form(form,email_list,str(docids),reply_to,smtp_server)
          else:
              print_form(input_page,doc_id,"1")
   return 0


if __name__=="__main__":
  sys.exit(main())

