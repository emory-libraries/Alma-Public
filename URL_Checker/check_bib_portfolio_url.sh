#!/bin/bash

##
##  check_bib_portfolio_url.sh receives a text file from the command line;
##    it converts file to a text file compatible with turbo_url_alma.pl .
## example of lines from input file:
# Bibliographic Record,990016345870302486,http://purl.access.gpo.gov/GPO/LPS125131
# Portfolio,53284293680002486,http://purl.access.gpo.gov/GPO/LPS125131
#
# corresponding lines to feed into turbo_url_alma.pl:
# http://purl.access.gpo.gov/GPO/LPS125131_|_990016345870302486_|_1
# http://purl.access.gpo.gov/GPO/LPS125131_|_532842936800024866_|_2
##   author: bernardo gomez 
##   date: february, 2018
if [ $# -lt 1 ]; then
   echo "ERROR check_bib_portfolio_url.sh: input file missing in command line." >&2
   echo "usage: check_bib_portfolio_url.sh input-file " >&2
   exit 1
fi
input_dir=pathtoalma/integrations/urlCheck/
output_dir=pathtoalma/integrations/urlCheck/
work_dir=pathtoalma/integrations/urlCheck/work/
config_dir=pathtoalma/config/
bin_dir=pathtoalma/bin/

file=$1

# change Bibliographic Record to "1"
# change Portfolio to "2"
 
  cat  ${file}| parse_csv -d","  |\
  sed -r 's/(.*?)_\|_(.*?)_\|_(.*?)/\3_\|_\2_\|_\1/g' | sed 's/Bibliographic Record/1/g'|\
  sed 's/Portfolio/2/g'| sort -u  > ${work_dir}input_all_urls

  turbo_url_alma.pl -i  ${work_dir}input_all_urls  -m ${config_dir}checkurl_mailing_list.txt -t ${work_dir} -n 6 -d 10  -e ${config_dir}url_check_exception.txt  2> ${work_dir}checkurl_log 
  filename=$(basename ${file})
  mv  ${file} ${input_dir}done_${filename}
  exit 0
