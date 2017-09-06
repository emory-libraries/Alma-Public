#!/bin/env python
# -*- coding: utf-8 -*-
"""
  this webservice streamlines a manual process involving 
  ALMA work orders.
  the webservice receives a list of barcodes corresponding
  to items that have received spine labels and it 
  perform two ALMA functions to place the item in the 
  final location.
"""
__author__ = 'bernardo gomez'
__contributor__ = 'alex cooper, laura trittin'
__date__ = 'may 2016'

import os
import sys
import re
import cgi
import time
import socket
import subprocess
import requests
import xml.etree.ElementTree as elementTree
import cgitb; cgitb.enable(display=1, logdir="/tmp")


def get_additional_info(xml_string):
    """
      this function parses the xml response from
      the API server and extracts the
      'additional_info' element.
      the response belongs to the SCAN operation.
      it returns element as a character string.
    """
    field_text=""
    outcome=1
    xml_string=xml_string.replace("\n","")
    try:
         tree=elementTree.fromstring(xml_string)
    except:
        sys.stderr.write("elementree failed(1)."+"\n")
        return "",1
    try:
          info_element=tree.find("additional_info")
    except:
        sys.stderr.write("couldn't get additional_info."+"\n")
        return "",1
    try:
        field_text=info_element.text
        if field_text == None:
           field_text=""
    except:
        sys.stderr.write("additional_info:couldn't get field text."+"\n")
        return "",1
    return field_text,0


def get_owning_library(xml_string):
    """
       this function receives an xml
       response from the API server
       and extracts the library name.
       the response corresponds to 
       the SCAN operation.
       it returns the library code 
       as a character string.
    """
    library=""
    outcome=1
    xml_string=xml_string.replace("\n","")
    try:
         tree=elementTree.fromstring(xml_string)
    except:
        sys.stderr.write("elementree failed(1)."+"\n")
        return "",1
    try:
          item_element=tree.find("item_data")
    except:
        sys.stderr.write("couldn't get item_data."+"\n")
        return "",1
    try:
        library=item_element.find("library").text
    except:
        sys.stderr.write("couldn't get library."+"\n")
        return "",1
    if library is None:
         sys.stderr.write("library field is empty."+"\n")
         return "",1
    else:
        outcome=0
    return library,outcome

def  scan_item_step2(item_url,apikey,library,circ_desk,done,auto_print_slip,place_on_hold_shelf,confirm,register):
   """
      this function performs an ALMA SCAN operation on an item.
   """
   response=""
   outcome=1

   headers={ 'Content-Type':'application/xml'}
   payload={'op':'SCAN','external_id':'false', 'library':library,'done':done,'auto_print_slip':auto_print_slip,'place_on_hold_shelf':place_on_hold_shelf,'confirm':confirm,'circ_desk':circ_desk,'register_in_house_use':register,'apikey':apikey}
   try:
      r=requests.post(item_url,params=payload, headers=headers)
   except:
      sys.stderr.write("http request failed:"+url+"\n")
      return "",1
   return_code=r.status_code
   if str(return_code) == "200":
     xml_string=r.content
     return xml_string,0
   else:
       sys.stderr.write("scan step2 failed:"+str(return_code)+" "+r.content+"\n")
       return "",1
   return "",1

def scan_item_step1(item_url,apikey,library,department,wo_type,done,auto_print_slip,place_on_hold_shelf,confirm,register):
   """
     this function performs a SCAN operation.
   """
   response=""
   outcome=1
# https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/9936522312302486/holdings/22305609290002486/items/23305609300002486?register_in_house_use=false&library=UNIV&done=true&place_on_hold_shelf=false&apikey=nnnnn&work_order_type=AcqWorkOrder&confirm=false&auto_print_slip=false&department=AcqDeptUNIV&external_id=false&op=SCAN

# {'register_in_house_use': 'false', 'library': 'UNIV', 'done': 'true', 'place_on_hold_shelf': 'false', 'apikey': 'nnnn', 'work_order_type': 'AcqWorkOrder', 'confirm': 'false', 'auto_print_slip': 'false', 'department': 'AcqDeptUNIV', 'external_id': 'false', 'op': 'SCAN'}
   headers={ 'Content-Type':'application/xml'}
   payload={'op':'SCAN','external_id':'false', 'library':library,'done':done,'auto_print_slip':auto_print_slip,'place_on_hold_shelf':place_on_hold_shelf,'confirm':confirm,'department':department,'work_order_type':wo_type,'register_in_house_use':register,'apikey':apikey}
#### the following hack would allow communication via port 443
   try:
      r=requests.post(item_url,params=payload, headers=headers)
   except:
      sys.stderr.write("http request failed:"+url+"\n")
      return "",1
   return_code=r.status_code
   if str(return_code) == "200":
     xml_string=r.content
     return xml_string,0
   else:
       sys.stderr.write("scan step1 failed:"+str(return_code)+" "+r.content+"\n")
       return "",1



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
      sys.stderr.write("finish_spine_process\n")
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


def get_record_info(url,apikey):
   """
     this function retrieves a
     URL that points to ALMA item
     information.
     it returns the URL.
   """
   response=""
   outcome=1
   payload={'apikey':apikey}
   try:
      r=requests.get(url,params=payload)
   except:
      sys.stderr.write("http request failed:"+url+"\n")
      return "",1
   return_code=r.status_code
   sys.stderr.write("return_code:"+str(return_code)+"\n")
   item_url=""
   if str(return_code) == "200":
     xml_string=r.content
     #xml_string=xml_string.replace("\n","")
     try:
         tree=elementTree.fromstring(xml_string)
     except:
        sys.stderr.write("elementree failed(1)."+"\n")
        return "",1
     try:
          item_url=tree.get("link")
     except:
        sys.stderr.write("couldn't get link."+"\n")
        return "",1

   else:
     sys.stderr.write("get_record failed:"+str(r.content)+"\n")
     return "",1
   return item_url,0

#library
#circ_desk_step2
#department
#wo_type

def process_form(form_file, max_file_size,result_file,source_file,url,apikey_get,apikey_post,mail_list,library_step1,circ_desk_step2,department,wo_type):
  """
     it receives all the fields from the web form 
     and additional variables to perform the 
     ALMA operations via the ALMA API.
  """
  workf_prefix="/tmp/process_spinomatic_"
  pid=str(os.getpid())
  workfile=workf_prefix+pid
  delim="	"
  if source_file.file:
    in_string=source_file.file.read()
    source_file.file.close()
 

  try:
       result=open(result_file,'w')
  except:
      print_failure(form_file,"ERROR: couldn't open result file.")
      return
  lines=in_string.split("\n")
  list=[]
  excel_buster="' "
  list.append("barcode"+delim+"outcome"+delim+"description"+delim+"recommendation"+delim+"\n")
  for barcode in lines:
      barcode=barcode.rstrip("\n")
      barcode=barcode.rstrip("\r")
      try:
          if barcode <> "":
            int(barcode)
      except:
          list.append(excel_buster+str(barcode)+delim+"ERROR"+delim+"barcode is not an integer"+""+delim+"\n")
          continue
      if str(barcode)  <> "":
         api_url=url+str(barcode)
         item_url,outcome=get_record_info(api_url,apikey_get)
         if outcome == 0:
  ##  process xml string
            library=library_step1
            circ_desk=""
            done="true"
            place_on_hold_shelf="false"
            confirm="false"
            register="false"
            auto_print_slip="false"
            register_in_house_use="false"
            response,outcome=scan_item_step1(item_url,apikey_post,library,department,wo_type,done,auto_print_slip,place_on_hold_shelf,confirm,register)
            if outcome == 0:
                library,outcome=get_owning_library(response)
                if outcome == 0:
                   circ_desk=circ_desk_step2
                   done="false"
                   response,outcome=scan_item_step2(item_url,apikey_post,library,circ_desk,done,auto_print_slip,place_on_hold_shelf,confirm,register)
                   if outcome == 0:
                      result_description,outcome=get_additional_info(response)
                      if outcome == 0:
                         list.append(excel_buster+str(barcode)+delim+"OK"+delim+str(result_description)+delim+""+delim+"\n")
                      else:
                         list.append(excel_buster+str(barcode)+delim+"ERROR"+delim+"couldn't parse result from second scan"+delim+"report to core-services"+delim+"\n")
                   else:
                        list.append(excel_buster+str(barcode)+delim+"ERROR"+delim+"second scan failed"+delim+"report to core-services"+delim+"\n")
                    
                else:
                   list.append(excel_buster+str(barcode)+delim+"ERROR"+delim+"couldn't get library code"+delim+"report to core-services"+delim+"\n")
            else:
               list.append(excel_buster+str(barcode)+delim+"ERROR"+delim+"first scan failed"+delim+"report to core-services"+delim+"\n")
         else:
           list.append(excel_buster+str(barcode)+delim+"ERROR"+delim+"bad barcode"+delim+"correct barcode"+delim+"\n")
  for entry in list:
     result.write(entry)
  result.close()
  #####os.unlink(workfile)
  if os.path.exists(result_file):

       command="finish_spine_process.sh "+result_file+" "+mail_list

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
       alma_url
       apikey_get
       apikey_post
       circ_desk_step2
       department
       directory
       file_prefix
       form_file
       library_step1
       max_file_size
       secretword
       sys_email
       wo_type
   
    it presents a webform to HTTP client.
    webform variables:
        secretword ( it acts a password);
        text file with barcodes;
        email address(es) to receive result.
    it sends email message via a shell script
     ( finish_spine_process.sh )
  """
  host=socket.gethostbyaddr(socket.gethostname())
  hostname=host[0]

  sys_email="alma"+"@"+hostname
  sys.stderr.write("sys_email:"+sys_email+"\n")
  if len(sys.argv)  < 2:
      print_failure("","Internal system failure. configuration file is missing.")
      return 1

  try:
        configuration=open(sys.argv[1], 'rU')
  except IOError:
        print_failure("","Internal system failure(1).")
        send_email("finish_spine_process",sys_email,"[finish_spine_process] system failure open config",sys.argv[1] )
        return 1
  sys_email="bgomez@emory.edu"
  form_file=""
  secretword=""
  max_file_size=""
  log_file_name=""
  directory=""
  file_prefix=""
  apikey=""
  alma_url=""
  library_step1=""
  circ_desk_step2=""
  department=""
  wo_type=""

  pat=re.compile("(.*?)=(.*)")
  for line in configuration:
      m=pat.match(line)
      if m:
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
         if m.group(1) == "alma_url":
              alma_url=m.group(2)
         if m.group(1) == "apikey_get":
              apikey_get=m.group(2)
         if m.group(1) == "apikey_post":
              apikey_post=m.group(2)
         if m.group(1) == "library_step1":
              library_step1=m.group(2)
         if m.group(1) == "circ_desk_step2":
              circ_desk_step2=m.group(2)
         if m.group(1) == "department":
              department=m.group(2)
         if m.group(1) == "wo_type":
              wo_type=m.group(2)
  fail=0
  if sys_email== "":
     host=socket.gethostbyaddr(socket.gethostname())
     hostname=host[0]
     sys_email="alma"+"@"+hostname
  if directory == "":
     send_email("finish_spine_process",sys_email,"[finish_spine_process] config. file didn't define directory",sys.argv[1] )
     fail+=1
  if file_prefix == "":
     send_email("finish_spine_process",sys_email,"[finish_spine_process] config. file didn't define file_prefix",sys.argv[1] )
     fail+=1
  if alma_url == "":
     send_email("finish_spine_process",sys_email,"[finish_spine_process] config. file didn't define api url",sys.argv[1] )
     fail+=1
  if form_file == "":
     send_email("finish_spine_process",sys_email,"[finish_spine_process] config. file didn't define form_file",sys.argv[1] )
     fail+=1
  if secretword == "":
     send_email("finish_spine_process",sys_email,"[finish_spine_process] config. file didn't define secretword",sys.argv[1] )
     fail+=1
  if max_file_size  == "":
     send_email("finish_spine_process",sys_email,"[finish_spine_process] config. file didn't define max_file_size",sys.argv[1] )
     fail+=1
  #if log_file_name == "":
     #send_email("finish_spine_process",sys_email,"[finish_spine_process] config. file didn't define log_file_name",sys.argv[1] )
     #fail+=1
  
  if fail > 0:
    print_failure("","Internal system failure(2).")
    return 1

  try:
    test_file=open(form_file,'rU')
    test_file.close()
  except:
    print_failure("","Internal system failure(3).")
    send_email("finish_spine_process",sys_email,"[finish_spine_process] can't open form file",sys.argv[1] )
    return 1


  os.environ["LANG"]="en_US.utf8"

  form = cgi.FieldStorage()
  outcome=quick_validation(form)
  pid=str(os.getpid())
  today_is=time.strftime('%Y%m%d',time.localtime())
  result_file=directory+"/"+file_prefix+today_is+"_"+pid+".xls"
  if outcome == 0:
    password=form.getfirst('secretword')
    if password != secretword:
       print_failure(form_file,"Secret word doesn't match")
       return 1
    source_file=form["source"]
    mail_list=form.getfirst("email")
    mail_list=re.sub(" +",",",mail_list)
    mail_list=mail_list.rstrip(",")

# library_step1=""
# circ_desk_step2=""
# department=""
# wo_type=""

    process_form(form_file,max_file_size,result_file,source_file,alma_url,apikey_get,apikey_post,mail_list,library_step1,circ_desk_step2,department,wo_type)
  #log_file.close()

  if outcome == 1:
    print_form(form_file,"")
    return

  if outcome > 100:
    print_form(form_file,"expected fields are missing.")
  return


if __name__ == "__main__":
  sys.exit(main())
  
