#!/bin/bash

bin_dir="/alma/bin/"
config="/alma/config/produce_deleted_records.cfg"
config2="/alma/config/produce_withdrawn_records.cfg"
config3="/alma/config/produce_deleted_items_list.cfg"
config_dir="/alma/config/"
error_log="/alma/integrations/oclc/delete/log/delete_oclc_log.$$"
error_log2="/alma/integrations/oclc/delete/log/delete_oclc_log2.$$"
error_log3="/alma/integrations/oclc/delete/log/delete_oclc_log3.$$"
log_parsed="/alma/integrations/oclc/delete/work/delete_oclc_log.txt"
log_parsed2="/alma/integrations/oclc/delete/work/delete_oclc_log2.txt"
log_parsed3="/alma/integrations/oclc/delete/work/delete_oclc_log3.txt"
results1="/alma/integrations/oclc/delete/work/delete_oclc_results1_$$.txt"
results2="/alma/integrations/oclc/delete/work/delete_oclc_results2_$$.txt"
results3="/alma/integrations/oclc/delete/work/delete_oclc_results3_$$.txt"
oclc_api_log="/alma/integrations/oclc/delete/log/oclc_api_$$"

mail_list="[emails]"
dow=$(date +%u)

####unset holdings for deleted titles
${bin_dir}get_alma_deleted_holdings.py ${config} 2> ${error_log} | ${bindir}oclc_delete_holdings.py ${config_dir}delete_oclc_holdings.cfg > ${results1} 2> ${oclc_api_log}
cat ${error_log} | grep exists >> ${log_parsed}
if [ -s ${log_parsed} ]; then
    if [ ${dow} == 1 ]; then
        mutt -a ${log_parsed} -s "Delete OCLC Holdings Report" -- ${mail_list} <<EOM
attached is today's log for deleted.
EOM

        rm ${log_parsed}
    fi

fi

####unset holdings for deleted items
${bin_dir}get_alma_deleted_items.py ${config3} 2> ${error_log3} | ${bindir}oclc_delete_holdings.py ${config_dir}delete_oclc_holdings.cfg > ${results3} 2> ${oclc_api_log}
cat ${error_log3} | grep exists >> ${log_parsed3}
if [ -s ${log_parsed3} ]; then
    if [ ${dow} == 1 ]; then
        mutt -a ${log_parsed3} -s "Delete OCLC Holdings Report" -- ${mail_list} <<EOM
attached is today's log for deleted.
EOM

        rm ${log_parsed3}
    fi

fi

####unset holdings for withdrawn titles
${bin_dir}get_alma_deleted_holdings.py ${config2} 2> ${error_log2} | ${bindir}oclc_delete_holdings.py ${config_dir}delete_oclc_holdings.cfg >  ${results2} 2>> ${oclc_api_log}
cat ${error_log2} | grep Alma >> ${log_parsed2}
if [ -s ${log_parsed2} ]; then
    if [ ${dow} == 1 ]; then
        mutt -a ${log_parsed2} -s "Withdrawn OCLC Holdings Report" -- ${mail_list} <<EOM
attached is today's log for withdrawn.
EOM

        rm ${log_parsed2}
    fi

fi

exit 0
