#!/bin/bash
# Name: Meyer SFTP
# Purpose: To see if files exist on the William B. Meyer SFTP server.
# Created: by Alex Cooper, on January, 2017

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

cd /alma/integrations/lsc/data_backup/

for file in *.CSV; do
    tar -czf ${file}.tar.gz ${file}
    rm ${file}
done

mail -s "Retrieval has finished" ${mail_list} <<EOM
  The weekly Meyer file backup completed.
EOM

exit 0
