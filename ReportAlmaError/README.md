**report_alma_error** is a webservice that receives a list of
one or more ALMA mms_ids and it presents a webform with two
input fields:
  - comment 
  - email 
 
 comment allows a PRIMO user to report an error or submit a 
 comment about the designated mms_id(s). the user can specify
 an email address to receive a reply from the technical services
 team. the email address is optional.

## Files:
 - report_alma_error.py
 - report_alma_error.cfg
 - report_alma_error.html
 - get_alma_bib.py
 - get_alma_bib.cfg
 
 **report_alma_error.py** and **get_alma_bib.py** are python scripts and they
 would reside in a bin directory.
 **report_alma_error.cfg** and **get_alma_bib.cfg** are configuration files and
 they would reside in a config directory.
 **report_alma_error.html** would reside in an webserver (apache) docs directory.
 
 
