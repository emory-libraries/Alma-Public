#!/bin/env python
# -*- coding: utf-8 -*-
r"""
  webservice that receives an mms_id, a callnumber, and a 
  holding library code, and it displays a webform 
  that would produce a text message for a cellular phone.
  the webform will prompt the user for a phone number and
  a cellular carrier name. a note field is optional.

  the webservice expects a configuration file on the 
  command line with the following variables:

     carrier_info
     failure_page
     get_record_url
     input_page
     result_page
     sys_email
     unknown_carrier_page
     short_libname
  the carrier name menu allows a "None of the above".
  the webform will  therefore present another form to 
  receive the name of the new carrier.
"""
__author__ = 'bernardo gomez'
__date__ = 'january 2016'

import os
import sys
import cgi
import cgitb; cgitb.enable(display=1, logdir="/tmp")
import marcxml
import requests
import urllib
import re
import time


def get_record(base_url,docid):
   """
     it invokes custom webservice to get alma's MARCXML, including
     items.
     it returns two objects: 
        marcxml string and outcome (0=success, 1= failure)
   """
   xml_string=""
   outcome=1
   request_string=base_url+str(docid)
   try:
      r=requests.get(request_string, timeout=10)
   except:
      sys.stderr.write("api request failed.couldn't get bib record. \n")
      return xml_string,1
   status=r.status_code
   if status == 200:
       xml_string=r.content
   else:
       return xml_string,1
   return xml_string,0


def get_bib_title(docid,get_record_url):
   """
     it invokes the custom get_alma_bib to 
     retrieve the bibliographic title.
   """  
   title=""
   outcome=1
   try:
     xml_string,outcome=get_record(get_record_url,docid)
   except:
     sys.stderr.write("error getting xml:"+"\n")
     return "",1
   #sys.stderr.write("get_bib_title: "+str(outcome)+"\n")
   if outcome == 0:
     in_string=xml_string.replace("\n","")
     try:
         record=marcxml.biblio(in_string)
     except:
         sys.stderr.write("failed\n")
         return
     title_list=record.get_field("245")
     for title in title_list:
      title_part_a=""
      title_part_b=""
      subfield=title.split("\\p")
      title=""
      for sf in subfield:
         if sf != "":
            if sf[0:1] == "a":
                  #title_part_a=str(sf[1:])
                  title_part_a=sf[1:]
                  if title_part_a.isdigit():
                    title_part_a=str(title_part_a)
            if sf[0:1] == "b":
                  #title_part_b=str(sf[1:])
                  title_part_b=sf[1:]
                  if title_part_b.isdigit():
                    title_part_b=str(title_part_b)
      title=title_part_a+" "+title_part_b
      title=title.replace("/","")
      #title=urllib.quote(title)

   return title,outcome


def quick_validation(form):
  """ form has not variables: outcome=1. fatal error
      form has no state variable: outcome=2 show input form.
      form has a state value, but carrier is NONE: outcome=3
      form has a state value, no carrier or no phone number: outcome=4
      form has a state value, it has  carrier and phone number: outcome=0
  """
  carrier=""
  phone_number=""
  if len(form) == 0:
        outcome=1   ### empty form. fatal error.
        return outcome
  if form.has_key("callnum") and form.has_key("doc_id") and form.has_key("library") and not form.has_key("state"):
	callnum=form.getfirst("callnum")
	doc_id=form.getfirst("doc_id")
        library=form.getfirst("library")
        state=form.getfirst("state")
        try:
           int(doc_id)
        except:
           return 6

	outcome=2  ## brand new request. show form.
        #sys.stderr.write(callnum+"|"+doc_id+"|"+library+"|"+str(state)+"|"+str(outcome)+"|"+'\n')
        return outcome
  if form.has_key("callnum") and form.has_key("title")  and form.has_key("library") and form.has_key("state"):
	callnum=form.getfirst("callnum")
        title=form.getfirst("title")
        library=form.getfirst("library")
        phone_number=form.getfirst("phone_number")
        state=form.getfirst("state")
        carrier=form.getfirst("carrier")
        if carrier == "NONE":
	   return 3   ### user chose "None of the above". show "new carrier".
	if phone_number is None:
           outcome=4
           #sys.stderr.write(callnum+"|"+title+"|"+library+"|"+str(state)+"|"+str(outcome)+"|"+'\n')
           return outcome    ## no phone number.
        if carrier is None:
           outcome=4
           #sys.stderr.write(callnum+"|"+title+"|"+library+"|"+str(state)+"|"+str(outcome)+"|"+'\n')
           return outcome    ## no carrier.
  #sys.stderr.write("form:"+str(form)+"\n")
  return 0

def print_error(message):
    """
      it prints an html page with an error message,
      as a result of fatal error.

    """
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""

    print "<!DOCTYPE html>"
    print "<html lang=\"en-US\">"
    print "<head>"
    print "<meta charset=\"utf-8\">"
    print "<meta name=\"viewport\" content=\"width=device-width\">"

    print "<title>Error message</title></head>"
    print "<body>"
    print "<h2>"+message+"</h2>"
    print "</body>"
    print "</html>"
    return 0

##
def print_success(file_name, callnum,title,library):
 """
  it prints an html page with bibliographic information.
 """
 try:
     file=open(file_name, 'r')
 except:
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    print ""
    print "<html>"
    print "<head><title>sendtophone. result</title></head>"
    print "<body>"
    print "<h2>"+message+"</h2>"
    print "</body>"
    print "</html>"
    return

 print '%s' % "Content-Type: text/html; charset=utf-8"
 print ""
 print ""
 for line in file:
        line=line.replace(r"<!--CALL_NUMBER=-->",callnum)
        line=line.replace(r"<!--TITLE=-->",title)
        line=line.replace(r"<!--LIBRARY=-->",library)
        print line
 file.close()
 return

##
def print_unknown_carrier_form(file_name, message):
 """
    it displays a webform to receive the name of a
    new cellular carrier.
    it receives the filename with html template, and
    the prompt text. 
 """ 
 try:
     file=open(file_name, 'r')
 except:
    print '%s' % "Content-Type: text/html; charset=utf-8"
    print ""
    print ""
    print "<html>"
    print "<head><title>sendtophone. unknown carrier</title></head>"
    print "<body>"
    print "<h2>"+message+"</h2>"
    print "</body>"
    print "</html>"
    return

 print '%s' % "Content-Type: text/html; charset=utf-8"
 print ""
 print ""
 for line in file:
          line=line.replace(r"<!--MESSAGE=-->",message)
	  print line
 file.close()
 return
##

def send_email(prog_name,email_list,subject,message,smtp_server):

  """
     it sends an email message.
     'prog_name' is not used here.
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
  sender="do-not-reply"+"@"+"kleene.library.emory.edu"

  msg['From'] = sender

# Establish an SMTP object and connect to your mail server
  s = smtplib.SMTP(smtp_server)
# Send the email - real from, real to, extra headers and content ...
  s.sendmail(sender,address, msg.as_string())
  s.quit()
  return


def print_form(file, message,callnum,title,phone_number,carrier,library):
	"""
	  it prints an html page with a web form.
          the 'file' argument has the file with 
          the webform template.
	"""
	print '%s' % "Content-Type: text/html; charset=utf-8"
	print ""
	time_stamp=time.time()
	time_stamp=int(time_stamp)
	time_stamp=str(time_stamp)
## <input  name="doc_id" type="hidden" value="">
        try:
           title=title[0:48]
        except:
           title="big oops!"

	for line in file:
	    if message <> "":
#<tr> <td class="feedback"><!--MESSAGE=--></td> </tr>
                s=re.search(r"<!--MESSAGE=-->",line)
	        if s:
                   msg="<tr> <td class=\"feedback\">"+message+"</td> </tr>\n"
                   print msg
	    line=line.replace(r"<!--SESSION=-->",time_stamp);
            try:
	       line=line.replace(r"<!--TITLE=-->",title);
            except:
	       line=line.replace(r"<!--TITLE=-->","ouch!");
	    line=line.replace(r"<!--LIBRARY=-->",library);
	    line=line.replace(r"<!--CALL_NUMBER=-->",callnum);
	    line=line.replace(r"<!--CARRIER=-->",carrier);
	    line=line.replace(r"<!--PHONE_NUMBER=-->",phone_number);
	    line=line.replace(r"<!--TITLE=-->",title);
	    print line
	return


def process_form(form,input_form,result_page,failure_page,carrier_dictionary,smtp_server,short_libname):
 """
    it  receives a form, it parses fields and it send email message
    to carrier. it also checks time stamp and empty field to catch
    spam robots.
    short_libname argument is a string with a list of abbreviated library names.

 """
 empty_result=[]
 empty_result.append("")
 phone_number=""
 carrier=""
 notes=""
 message=""
 callnum=""
 title=""
 if form.has_key("title"):
	title=form.getfirst("title")
 if form.has_key("title"):
	title=form.getfirst("title")
 if form.has_key("callnum"):
	callnum=form.getfirst("callnum")
 if form.has_key("library"):
	library=form.getfirst("library")
 if form.has_key("phone_number"):
	phone_number=form.getfirst("phone_number")
 if form.has_key("library"):
	library=form.getfirst("library")
 if form.has_key("carrier"):
        carrier=form.getfirst("carrier")
 if form.has_key("session"):
        session=form.getfirst("session")
	time_stamp=int(session)
	time_now=int(time.time())
   ## if form comes back in fewer than 3 seconds, call it a robot.
	if time_now - time_stamp >0 and time_now - time_stamp < 3:
   ## detected a spam robot.
           print_success(result_page,"","","")
   ## do not send text message.
	   return
 if form.has_key("mynotes"):
        notes=form.getfirst("mynotes")
 ## 
 if form.has_key("email2"):
   ## honeypot caught a suspect
        print_success(result_page,"","","")
   ## do not send text message.
	return
 phone_number=phone_number.strip();
 m=re.match("\d{10}",phone_number)

 if not m:
   print_form(input_form,"Phone number must have 10 digits",callnum,title,phone_number,carrier,library)
   return
    
 try:
        carrier_email=carrier_dictionary[carrier]
 except:
        print_form(input_form,"please, enter carrier's name",callnum,title,phone_number,carrier,library)
#	send_email("sendtophone",sys_email,"[sendtophone] missing carrier definition ","carrier "+carrier+" undefined")
	return
  
##
 message_body=""
 library_name={}
 name_list=short_libname.split(";")
 for element in name_list:
     code,name=element.split(":")
     library_name[code]=name
 try:
     lib_name=library_name[library]
 except:
     lib_name=library
 if notes == "":
   message_body=callnum+"\n"+" Title:"+title+"\n"
 else:
   message_body=callnum+"\n Title:"+title+"\n"+notes
 subject_line=lib_name+" callnumber"
 subscriber_address=phone_number+carrier_email
## sys.stderr.write("subscriber:"+subscriber_address+'\n')
 send_email("sendtophone",subscriber_address,subject_line,message_body,smtp_server)
 print_success(result_page,callnum,title,lib_name)
 return

def main():

  #sys_email="sirsi@euclidtest1.cc.emory.edu,bgomez@emory.edu"
  sys_email="sirsi@euclidtest1.cc.emory.edu"

  no_config_file="configuration file is missing"
  no_input_page="form file is missing"
  no_result_page="result file is missing"
  no_carrier_page="unknown carrier file is missing"
  no_unknown_carrier_page="unknown carrier file is missing"
  no_carrier_list="carrier list is missing in config. file"
  empty_result=[]
  empty_result.append("")
  failure_page=""
  title=""

  if (len(sys.argv) < 2):
	print_error("Internal system failure. no configuration file.")
	#send_email("sendtophone",sys_email,"[sendtophone] system failure", no_config_file)
	return 1

  try:
	configuration=open(sys.argv[1], 'r')
  except IOError:
	print_error("Internal system failure. couldn't open config. file")
	#send_email("sendtophone",sys_email,"[sendtophone] system failure open config",sys.argv[1] )
	return 1
  

  input_page=""
  result_page=""
  failure_page=""
  unknown_carrier_page=""
  callnum=""
  doc_id=""
  title=""
  carrier=""
  library=""
  phone_number=""
  carrier_info=""
  sys_email=""
  get_record_url=""
  smtp_server=""
  short_libname=""
  pat=re.compile("(.*?)=(.*)")
  for line in configuration:
	m=pat.match(line)
	if m:
		if m.group(1) == "input_page":
			input_page=m.group(2)
		if m.group(1) == "get_record_url":
			get_record_url=m.group(2)
		if m.group(1) == "result_page":
			result_page=m.group(2)
## att==@txt.att.net;verizon==@vtext.com;t-mobile==@tmomail.net;metropcs==@mymetropcs.com;sprint==@messaging.sprintpcs.com;virgin_mobile==@vmobl.com;
		if m.group(1) == "failure_page":
			failure_page=m.group(2)
		if m.group(1) == "unknown_carrier_page":
			unknown_carrier_page=m.group(2)
		if m.group(1) == "sys_email":
			sys_email=m.group(2)
		if m.group(1) == "smtp_server":
			smtp_server=m.group(2)
		if m.group(1) == "carrier_info":
			carrier_info=m.group(2)
		if m.group(1) == "short_libname":
			short_libname=m.group(2)
##			sys.stderr.write(input_page+'\n')

  if (input_page == ""):
	print_error("Internal system failure. form file is missing")
	#send_email("sendtophone",sys_email,"[sendtophone] no form file ",no_input_page )
	return 1
  if (result_page == ""):
	print_error("Internal system failure. result file is missing.")
	#send_email("sendtophone",sys_email,"[sendtophone] no result file ",no_result_page )
        return 1
  if (short_libname == ""):
	print_error("Internal system failure. short_libname file is missing.")
	#send_email("sendtophone",sys_email,"[sendtophone] no result file ",no_result_page )
        return 1
  if (unknown_carrier_page == ""):
	print_error("Internal system failure. unknown_carrier file is missing.")
	#send_email("sendtophone",sys_email,"[sendtophone] no unknown carrier page ",no_unknown_carrier_page )
        return 1
  if (carrier_info == ""):
	print_error("Internal system failure. carrier_info is missing.")
	#send_email("sendtophone",sys_email,"[sendtophone] no carrier list ",no_carrier_list )
        return 1
  if (smtp_server == ""):
	print_error("Internal system failure. smtp_server is missing.")
	#send_email("sendtophone",sys_email,"[sendtophone] no carrier list ",no_carrier_list )
        return 1
  try:
	input_form=open(input_page,'r')
  except IOError:
	print_error("Internal system failure. couldn't open input form.")
	#send_email("sendtophone",sys_email,"[sendtophone] couldn't open form file ",input_page )
	return 1
  try:
	result_file=open(result_page,'r')
  	result_file.close()
  except IOError:
	print_error("Internal system failure. couldn't open result page.")
	#send_email("sendtophone",sys_email,"[sendtophone] couldn't open result file ",result_page )
	return 1

  try:
	failure_file=open(failure_page,'r')
	failure_file.close()
  except IOError:
  	failure_page=""
	print_error("Internal system failure. couldn't open failure page.")
	#send_email("sendtophone",sys_email,"[sendtophone] couldn't open failure  file ",failure_page )
	return 1
# os.environ["LANG"]="en_US.utf8"
# PYTHONIOENCODING=utf_8
# os.environ["PYTHONIOENCODING"]="utf_8"

  carrier_list=carrier_info.split(";")
  carrier_dictionary={}
  for carrier in carrier_list:
     s=re.search("(.*)==(.*)",carrier)
     if s:
       carrier_name=s.group(1)
       carrier_email=s.group(2)
       carrier_dictionary[carrier_name]=carrier_email

  form = cgi.FieldStorage()

  outcome=quick_validation(form)
  #sys.stderr.write("quick_validation:"+str(outcome)+"\n")
  phone_number=""
  carrier=""
  if outcome == 0:
    process_form(form,input_form,result_page,failure_page,carrier_dictionary,smtp_server,short_libname)
    input_form.close()
    return 0
  if outcome == 1:
    print_error("title,callnum,library are missing.")
    input_form.close()
    return 1
  if outcome == 2:
## 
    callnum=form.getfirst("callnum")
    doc_id=form.getfirst("doc_id")
    library=form.getfirst("library")
    carrier=""
    phone_number=""
    #sys.stderr.write(str(title)+" "+str(get_record_url)+"\n")
    title,outcome=get_bib_title(doc_id,get_record_url)
    print_form(input_form,"",callnum,title,phone_number,carrier,library)
    input_form.close()
    return 1
  if outcome == 3:
    input_form.close()
    print_unknown_carrier_form(unknown_carrier_page,"Please enter the cell provider name and we will add it to the list.")
    return 1
  if outcome == 4:
    #sys.stderr.write("no phone# or carrier"+"\n")
    callnum=form.getfirst("callnum")
    title=form.getfirst("title")
    library=form.getfirst("library")
    carrier=form.getfirst("carrier")
    phone_number=form.getfirst("phone_number")
    if phone_number is None:
       phone_number=""
    if carrier is None:
       carrier=""
    title,outcome=get_bib_title(doc_id,get_record_url)
    print_form(input_form,"Phone number or carrier name is missing",callnum,title,phone_number,carrier,library)
    input_form.close()
    return 1
  if outcome == 6:
    print_error("doc_id is invalid.")
    input_form.close()
    return 1
     
  print_form(input_form,"",callnum,title,phone_number,carrier,library)
  #send_email("sendtophone",sys_email,"[sendtophone] form validation","undefined outcome value")
  input_form.close()
  return

if __name__=="__main__":
  sys.exit(main())
 
