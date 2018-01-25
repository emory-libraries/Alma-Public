#!/bin/bash
# Name: Meyer SFTP

config="/alma/config/" 
. ${config}environ     # dot in environ variables

# export all of the environ variables to my children
for env_var in $(cat ${config}environ | awk -F'=' '{print $1}')
do
  export ${env_var}
done

mail_list="acoope5@emory.edu"
script="/alma/bin/meyer_sftp.py"

${script}

mail -s "Retrieval has finished" ${mail_list}

exit 0
