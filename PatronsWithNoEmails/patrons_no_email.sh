#!/bin/bash

todays_date=$(date +"%Y%m%d")
dow=$(date +%w)
mail_list="[email]"
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
