#!/bin/bash
###
##  curl_to_checkurl.sh reads a text line from standard input;
##  it extracts the URL and it invokes curl to test the HTTP connection.
##  it writes the result to standard output.
##   input line format: URL_|_alma_mms_id_|_resource_type code_|_
##   output line format: HTTP1.1_|_return_code_|_extra text_|_input_line
##  
##  Author: bernardo gomez
##  Date: february, 2018
### 


function givehelp() {
  echo "$0 [-t seconds]"  >&2
  echo "$0   reads a checkurl line on standard input; " >&2
  echo "it calls curl with the given url and it writes a line with result on standard output" >&2
}

time_out=20
while getopts "t:h:w:" opt; do
  case "${opt}" in
     t) 
       time_out=${OPTARG}
       ;;
     h) 
       hostname=${OPTARG}
       ;;
     w) 
       response_file=${OPTARG}
       ;;
     *)
       givehelp
       exit 1
       ;;
  esac
done
#echo "${response_file}"
header=/tmp/header_curl_$$
while read line; do
  http_user_agent="User-Agent: Mozilla/5.0 (Linux; Redhat 7) UrlChecker/2.0"
  http_connection="Connection: Close"
  http_accept="Accept: */*"
  http_accept_language="Accept-Language: en-US;en;q=0.5"
  http_host="Host: ${hostname}"
  cat /dev/null > ${header}
  curl -m ${time_out}  --connect-timeout  ${time_out} -H "${http_accept}" -H "${http_host}" -H "${http_connection}"  -D ${header} "${line}"  > /dev/null 2> /dev/null
  status=$?
  if [ ${status} -ne 0 ]; then
        exit ${status}
  fi
  cat  ${header} > ${response_file}
  rm -f ${header}
done
exit 0

#      1      Unsupported protocol. This build of curl has no support for this protocol.
#      2      Failed to initialize.
#      3      URL malformed. The syntax was not correct.
#      5      Couldn’t resolve proxy. The given proxy host could not be resolved.
#      6      Couldn’t resolve host. The given remote host was not resolved.
#      7      Failed to connect to host.
#      8      FTP weird server reply. The server sent data curl couldn’t parse.
#      9      FTP  access denied. The server denied login or denied access to the particu-
#             lar resource or directory you wanted to  reach.  Most  often  you  tried  to
#             change to a directory that doesn’t exist on the server.
#      11     FTP  weird  PASS  reply.  Curl  couldn’t  parse  the  reply sent to the PASS
#             request.
#      13     FTP weird PASV reply, Curl  couldn’t  parse  the  reply  sent  to  the  PASV
#             request.
#      14     FTP weird 227 format. Curl couldn’t parse the 227-line the server sent.
#      15     FTP can’t get host. Couldn’t resolve the host IP we got in the 227-line.
#      17     FTP couldn’t set binary. Couldn’t change transfer method to binary.
#      18     Partial file. Only a part of the file was transferred.
#      19     FTP  couldn’t  download/access the given file, the RETR (or similar) command
#             failed.
#      28     Operation  timeout.  The  specified time-out period was reached according to
#             the conditions.

