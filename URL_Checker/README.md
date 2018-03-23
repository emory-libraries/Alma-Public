 **checkurls.sh** is a shell script that reads MARC files from a given directory; it converts the MARC files 
to text format; it extracts the record key (alma mms_id) and the  MARC 856 fields and invokes turbo_url_alma.pl that divides the 
list of URLs into several chunks and creates a process to check the URLs in each chunk. the url checking tool is "curl".

**check_bib_portfolio_url.sh** is a shell script that receives a CSV file from the command line; it converts the input lines
into lines compatible with turbo_url_alma.pl .  The CSV file contains URLs from ALMA portfolios and URLs from ALMA bibliographic records.

**checkurl_mailing_list.txt** is a configuration file that turbo_url_alma.pl expects to send email messages with failed
URLs. turbo_url_alma.pl separates ALMA portfolio URLs from ALMA bibliographic URLs when sending email messages.å



