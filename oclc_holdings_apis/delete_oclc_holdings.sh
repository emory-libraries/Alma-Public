#!/bin/bash

bin_dir="/alma/bin/"
config="/alma/config/produce_deleted_records.cfg"
config2="/alma/config/produce_withdrawn_records.cfg"
error_log="/tmp/delete_oclc_log.$$"
error_log2="/tmp/delete_oclc_log2.$$"
log_parsed="/tmp/delete_oclc_log.txt"
log_parsed2="/tmp/delete_oclc_log2.txt"
mail_list="acoope5@emory.edu egrant7@emory.edu"

####unset holdings for deleted titles
${bin_dir}delete_oclc_holdings_api.py ${config} 2> ${error_log}
cat ${error_log} | grep exists > ${log_parsed}
mutt -a ${log_parsed} -s "Delete OCLC Holdings Report" -- ${mail_list} <<EOM
attached is today's log for deleted.
EOM

####unset holdings for withdrawn titles
${bin_dir}delete_oclc_holdings_api.py ${config2} 2> ${error_log2}
cat ${error_log2} | grep Alma > ${log_parsed2}
mutt -a ${log_parsed} -s "Withdrawn OCLC Holdings Report" -- ${mail_list} <<EOM
attached is today's log for withdrawn.
EOM

exit 0
