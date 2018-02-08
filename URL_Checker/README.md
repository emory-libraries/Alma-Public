**checkurls.sh** is a shell script that reads MARC files from a given directory; it converts the MARC files 
to text format; it extracts the record key (alma mms_id) and the  MARC 856 fields and invokes turbo_url_alma.pl that divides the 
list of URLs into several chunks and creates a process to check the URLs.
the url checking is based on "curl".




