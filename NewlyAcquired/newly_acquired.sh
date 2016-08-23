#!/bin/bash
#Author: Alex C.
#Purpose: run scripts to add and remove 598 $$aNEW
#Date: 08/04/2016

alma_environ="/alma/config/environ"
. ${alma_environ}  # include environment file
# export all of the environ variables to my children
for env_var in $(cat ${alma_environ} | awk -F'=' '{print $1}')
do
  export ${env_var}
done

config="/alma/config/produce_new_list.cfg"
config2="/alma/config/update_new_books.cfg"
new_titles="/alma/integrations/new_books/primo/new_titles/"
work="/alma/integrations/new_books/primo/work/"
pending="/alma/integrations/new_books/primo/pending/in_process_books"
todays_date=$(date +"%Y%m%d")
bindir="/alma/bin/"
work_file="${work}new_pending_${todays_date}"
errorlog1="/tmp/new_acq_err1_$$.log"
errorlog2="/tmp/new_acq_err2_$$.log"
errorlog3="/tmp/new_acq_err3_$$.log"
errorlog4="/tmp/new_acq_err4_$$.log"
errorlog5="/tmp/new_acq_err5_$$.log"
errorlog6="/tmp/new_acq_err6_$$.log"
errorlog7="/tmp/new_acq_err7_$$.log"
mail_list=""
apikey=""

${bindir}new_items_analytics_list.py ${config} > ${work}work_file_${todays_date} 2> $errorlog1

if [ -f ${work}work_file_${todays_date} ]; then
    if [ -s ${work}work_file_${todays_date} ]; then
        cat ${work}work_file_${todays_date} | ${bindir}new_items_create_xml.py > ${work}work_file_parsed_${todays_date} 2> $errorlog2
    else
        mutt -s ${work}work_file_${todays_date} -- ${mail_list} <<EOM
File ${work}work_file_${todays_date} was not created today.
EOM
    fi
else
    mutt -s ${work}work_file_${todays_date} -- ${mail_list} <<EOM
File ${work}work_file_${todays_date} was not created today.
EOM
fi

if [ -f ${work}work_file_parsed_${todays_date} ]; then
    if [ -s ${work}work_file_parsed_${todays_date} ]; then
        cat ${work}work_file_parsed_${todays_date} | ${bindir}new_and_pending.py > ${work}new_mms_ids_${todays_date} 2> $errorlog3
    else
        mutt -s ${work}work_file_parsed_${todays_date} -- ${mail_list} <<EOM
File ${work}work_file_parsed_${todays_date} was not created today.
EOM
    fi
else
    mutt -s ${work}work_file_parsed_${todays_date} -- ${mail_list} <<EOM
File ${work}work_file_parsed_${todays_date} was not created today.
EOM
fi

if [ -f ${work}new_mms_ids_${todays_date} ]; then
    if [ -s ${work}new_mms_ids_${todays_date} ]; then
        ${bindir}new_and_pending.sh ${work}new_mms_ids_${todays_date} 2> ${errorlog4}
    else
        mutt -s ${work}new_mms_ids_${todays_date} -- ${mail_list} <<EOM
File ${work}new_mms_ids_${todays_date} was not created today.
EOM
    fi
else
    mutt -s ${work}new_mms_ids_${todays_date} -- ${mail_list} <<EOM
File ${work}new_mms_ids_${todays_date} was not created today.
EOM
fi

if [ -f ${pending} ]; then
    if [ -s ${pending} ]; then
        cat ${pending} | ${bindir}new_check_pending.py ${apikey} > ${work}new_pending_${todays_date} 2> ${errorlog5}
    else
        mutt -s ${pending} -- ${mail_list} <<EOM
File ${pending} was not created today.
EOM
    fi
else
    mutt -s ${pending} -- ${mail_list} <<EOM
File ${pending} was not created today.
EOM
fi

${bindir}new_pending_items_process.sh

if [ -f ${new_titles}new_mms_ids_${todays_date} ]; then
    if [ -s ${new_titles}new_mms_ids_${todays_date} ]; then
        cat ${new_titles}new_mms_ids_${todays_date} | ${bindir}new_items_put.py ${config2} 2> ${errorlog6}
    else
        mutt -s "${work}new_mms_ids_${todays_date}" -- ${mail_list} <<EOM
File ${work}new_mms_ids_${todays_date} was not created today.
EOM
    fi
else
    mutt -s "${work}new_mms_ids_${todays_date}" -- ${mail_list} <<EOM
File ${work}new_mms_ids_${todays_date} was not created today.
EOM
fi

if [ -f ${work_file} ]; then
    if [ -s ${work_file} ]; then
        ${bindir}old_items.sh 2> ${errorlog7}
    else
        mutt -s "${work_file}" -- ${mail_list} <<EOM
File ${work_file} was not created today.
EOM
    fi
else
    mutt -s "${work_file}" -- ${mail_list} <<EOM
File ${work_file} was not created today.
EOM
fi

exit 0
