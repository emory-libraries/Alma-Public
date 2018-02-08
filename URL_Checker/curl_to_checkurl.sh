#!/bin/bash

###
##  curl_to_checkurl.sh reads a text line from standard input;
##  it extracts the URL and it invokes curl to test the HTTP connection.
##  it writes the result to standard output.
##   input line format: URL|alma_mms_id|library_code|
##   output line format: HTTP1.1|return_code|extra text|input_line
##
##  Author: bernardo gomez
##  Date: february, 2018
###

givehelp() {
  echo "$0 [-t seconds]"  >&2
  echo "$0   reads a checkurl line on standard input; " >&2
  echo "it calls curl with the given url and it writes a line with result on standard output" >&2
}

time_out=20
while getopts "t:" opt; do
  case "${opt}" in
     t) 
       time_out=${OPTARG}
       ;;
     *)
       givehelp
       exit 1
       ;;
  esac
done
header=/tmp/header_curl_$$
while read line; do
  IFS="|"; read -ra FIELD <<< "${line}"
  if [ ${#FIELD[@]} -lt 3 ]; then
     echo "HTTP1.1|609|Line is too short for url checker||${line}"
     exit 1
  fi
  url=${FIELD[0]}
  if [[ ${url} =~ (http://)(.*) || ${url} =~ (https://)(.*)  ]]; then
     strresult=${BASH_REMATCH[1]}
  else
     echo "HTTP1.1|606|Ill-formed URL||${line}"
     exit 1
  fi
  cat /dev/null > ${header}
  curl -m ${time_out} --connect-timeout ${time_out} -D ${header} "${url}" 2> /dev/null > /dev/null 
  status=$?
  if [ ${status} -ne 0 ]; then
     if [ ${status} -eq 6 ]; then
        echo "HTTP1.1|603|Hostname not found||${line}"
        continue
     elif [ ${status} -eq 28 ]; then
        echo "HTTP1.1|605|Timeout||${line}"
        continue
     else 
        echo "HTTP1.1|604|defective response (curl code=${status}||${line}"
        continue
     fi
     
  fi
  #cat ${header} >&2
  response=$(cat ${header} | urlchecker_parse_header.py| tr -d '\n' )
  status=$?
  if [ ${status}  -eq 0 ]; then
      echo "${response}|${line}"
  fi
done
exit 0
