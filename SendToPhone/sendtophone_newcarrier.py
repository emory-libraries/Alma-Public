#!/bin/env python
r"""
   sendtophone_newcarrier is a webservice that presents
   a webform to receive from a user the name of
   a cellular carrier that is not part of the list
   of carriers in the the sendtophone_individual 
   webservice. 
  
"""
__author__ = "bernardo gomez"
__date__ = 'january 2011'

import os
import sys
import cgi
import cgitb; cgitb.enable(display=1, logdir="/tmp")
import re
import time

def print_failure(file_name, message):
 """
  it prints an html page with an error message.
 """
 try:
     file=open(file_name, 'r')
 except:
     file_name=""
 if file_name == "":
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
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
    print ""
    pat_message=re.compile("<!--MESSAGE=-->")
    for line in file:
	str=pat_message.search(line)
	if str:
## print result
	 	print "<h2>"+message+"</h2>"
		print "<hr>"
	else:
	  	print line,
    file.close()

 return

##
def print_success(file_name, message):
 """
   it sends a message to the web client.
   'file_name' is the name of the html
   template;
   'message' is the message text.
 """
 try:
     file=open(file_name, 'r')
 except:
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    print ""
    print "<html>"
    print "<head><title>digitize me. result</title></head>"
    print "<body>"
    print "<h2>"+message+"</h2>"
    print "</body>"
    print "</html>"
    return

 print '%s' % "Content-Type: text/html; charset=utf-8"
 print ""
 print ""
 pat_title=re.compile("<!--TITLE=-->")
 pat_call_number=re.compile("<!--CALL_NUMBER=-->")
 for line in file:
        s=pat_title.search(line)
        if s:
          line=line.replace(r"<!--TITLE=-->",line)
	  print line
	  continue
        s=pat_call_number.search(line)
        if s:
          line=line.replace(r"<!--CALL_NUMBER=-->",line)
	  print line
          continue
        print line
 file.close()
 return

def send_email(email_list,subject,message,smtp_server):

  """
     it composes an error message and sends it out.

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
  sender="do-not-reply"+"@"+"mail.library.emory.edu"

  msg['From'] = sender

# Establish an SMTP object and connect to your mail server
  s = smtplib.SMTP(smtp_server)
# s.connect("localhost")
# Send the email - real from, real to, extra headers and content ...
  s.sendmail(sender,address, msg.as_string())
  s.quit()
  return

####

def print_form(file, message,result):
	"""
	  it prints an html page with a web form.
          'file' is the html file.
	"""
	print '%s' % "Content-Type: text/html; charset=utf-8"
	print ""
	print ""
	for line in file:
	  	print line
	return

def process_form(form,input_form,result_file,failure_page,smtp_server):
 """
    it receives the http variables in 'form' object.
    'input_form' is the file with an html template.
    'failure_page' is the file with an html template.
    'smtp_server' holds the email hostname.
 """
 empty_result=[]
 empty_result.append("")
 selcatalog_failed="selcatalog failed"
 phone_number=""
 carrier=""
 catkey=""
 library=""
 notes=""
 message=""
 sys.stderr.write("carrier:"+carrier+'|\n')
 if form.has_key("carrier"):
        carrier=form.getfirst("carrier")
 ## 
 message_body="add "+carrier+" to the carrier list.\n"
 
 send_email(sys_email,"sendtophone: unknown carrier",message_body,smtp_server)
 print_success(result_file,message_body)
 return

def main():
  """ It sets the unicorn environment.
	It shows the input form if input fields are empty.
	It processes the form if there is at least one
	input field.
	The networkID has precedence.
  """
  global no_carrier_page,sys_email

  #sys_email="sirsi@mail.library.emory.edu,bgomez@emory.edu"
  sys_email="sirsi@mail.library.emory.edu"
  request_email="sirsi@mail.library.emory.edu"

  no_config_file="configuration file is missing"
  no_unicorn_env="failed to set unicorn environment"
  no_input_page="form file is missing"
  no_result_page="result file is missing"
  no_carrier_page="unknown carrier file is missing"
  no_unknown_carrier_page="unknown carrier file is missing"
  no_carrier_list="carrier list is missing in config. file"
  empty_result=[]
  empty_result.append("")
  failure_page=""

# try:
#   unicorn_environment.set_environment("/s/sirsi/Unicorn/Config")
# except:
#    print_failure(failure_page,"Internal system failure.")
#    send_email(sys_email,"[sendtophone] system failure",no_unicorn_env)
#    return 1

  if (len(sys.argv) < 2):
	print_failure(failure_page,"Internal system failure. No configuration file.")
	return 1

  try:
	configuration=open(sys.argv[1], 'r')
  except IOError:
	print_failure(failure_page,"Internal system failure. Couldn't open configuration file.")
	return 1
  


  input_page=""
  result_page=""
  failure_page=""
  unknown_carrier_page=""
  call_number=""
  catkey=""
  carrier=""
  phone_number=""
  carrier_list=[]
  tempdir=""
  smtp_server=""
  pat=re.compile("(.*?)=(.*)")
  for line in configuration:
	m=pat.match(line)
	if m:
		if m.group(1) == "input_page":
			input_page=m.group(2)
		if m.group(1) == "result_page":
			result_page=m.group(2)
		if m.group(1) == "failure_page":
			failure_page=m.group(2)
		if m.group(1) == "unknown_carrier_page":
			unknown_carrier_page=m.group(2)
		if m.group(1) == "tempdir":
			tempdir=m.group(2)
		if m.group(1) == "sys_email":
			sys_email=m.group(2)
		if m.group(1) == "smtp_server":
			smtp_server=m.group(2)
		if m.group(1) == "carrier_list":
			carrier_list=m.group(2)
##			sys.stderr.write(input_page+'\n')

  if (input_page == ""):
	print_failure(failure_page,"Internal system failure. no form file.")
	return 1

  if (result_page == ""):
	print_failure(failure_page,"Internal system failure. no result file.")
  if (unknown_carrier_page == ""):
	print_failure(failure_page,"Internal system failure. no html file.")
  if (carrier_list == ""):
	print_failure(failure_page,"Internal system failure. no carrier list.")
  if (smtp_server == ""):
	print_failure(failure_page,"Internal system failure. no smtp server.")
  try:
	input_form=open(input_page,'r')
  except IOError:
	print_failure(failure_page,"Internal system failure. couldn't open form file.")
	return 1
  try:
	result_file=open(result_page,'r')
  	result_file.close()
  except IOError:
	print_failure(failure_page,"Internal system failure. couldn't open result html file.")
	return 1

  try:
	failure_file=open(failure_page,'r')
	failure_file.close()
  except IOError:
  	failure_page=""
	print_failure(failure_page,"Internal system failure. couldn't open html fail page.")
	return 1
  os.environ["LANG"]="en_US.utf8"

    ## sys.stderr.write("getting form"+'\n')

  ## example carrier list with sms gateway: att==@txt.att.net;verizon==@vtext.com;t-mobile==@tmomail.net;
  form = cgi.FieldStorage()
### 
  if len(form) == 0:
          print_form(input_form,"",empty_result)
	  return
  if  form.has_key("carrier"):
     carrier=form.getfirst("carrier")
### 
###     sys.stderr.write("carrier==>"+carrier+'\n')
     process_form(form,input_form,result_page,failure_page,smtp_server)
     return
  input_form.close()

  return 0

if __name__=="__main__":
  sys.exit(main())
  
