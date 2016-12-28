#!/bin/bash

alma_environ="/alma/config/environ"
. ${alma_environ}  # include environment file
# export all of the environ variables to my children
for env_var in $(cat ${alma_environ} | awk -F'=' '{print $1}')
do
  export ${env_var}
done

todays_date=$(date +"%Y%m%d")
dow=$(date +%w)
#mail_list="acoope5@emory.edu"
mail_list="acoope5@emory.edu,jperlov@emory.edu"
bindir="/alma/bin/"
script=${bindir}patrons_no_email_api.py
configdir="/alma/config/"
config=${configdir}patrons_no_email.cfg
report="/tmp/patrons_without_emails_${todays_date}.csv"

if [ ${dow} -eq 1 ]; then
    echo "EmplId,Email,First Name,Last Name,Patron Group,Status Date,Expiry Date" > ${report}
    ${script} ${config} >> ${report}
    mutt -a ${report} -s "Patrons With Out Email Addresses" -- ${mail_list} <<EOM
    See attachment.
EOM
fi

exit 0
