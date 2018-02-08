#!/bin/bash

## checkurls.sh reads MARC files from a given directory;
##  it converts a MARC file to text format to extract 
##  the alma mms_id and the 856 fields from the records.
##  it invokes turbo_url_alma.pl to check the URLs that
##  reside in the records.
##  turbo_url_alma.pl expects a file with a mailing list.
##  the lists of defective URLs are mailed to the mailing list.
##
##  author: bernardo gomez
##  date: february 2018
##
input_dir=path_to/integrations/urlCheck/
output_dir=path_to/integrations/urlCheck/
work_dir=path_to/integrations/urlCheck/work/
config_dir=path_to/config/
email_list="someone@emory.edu"
bin_dir=path_to/bin/

for file in ${input_dir}input_marc_*; do
   cat ${file}| marc_to_txt | select_urls.py 2> ${work_dir}invalid_urls_$$ |sort  > ${work_dir}input_urls_$$
   turbo_url_alma.pl -i  ${work_dir}input_urls_$$ -m ${config_dir}checkurl_mailing_list.txt -t ${work_dir} -n 6  2> ${work_dir}checkurl_log 
   if [ -s {${work_dir}invalid_urls_$$} ]; then
      mail -s "check_urls: invalid 856 fields" ${email_list}  -a ${work_dir}invalid_urls_$$ <<EOM
      attached is the list.
EOM
   fi
   filename=$(basename ${file})
   mv  ${file} ${input_dir}/done_${filename}
done
exit 0
