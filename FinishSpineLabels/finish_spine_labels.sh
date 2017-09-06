#!/bin/bash

### 
# shell script that sends a file as an attachment
# to a designated list of email addresses.
# author= 'bernardo gomez'
# date= 'may 2016'
###
config="/sirsi/webserver/config/" 
. ${config}environ     # dot in environ variables

# export all of the environ variables to my children
for env_var in $(cat ${config}environ | awk -F'=' '{print $1}')
do
  export ${env_var}
done

if [ $# -lt 2 ]; then
   echo "missing result file or email address" >&2
   exit 1
fi
result=$1
email_list=$2

if [ -s ${result} ]; then
      mailx -s"spine label batch" -a ${result} ${email_list} <<EOM
   attachment contains results.
EOM
fi
exit 0
