#!/bin/bash

alma_environ="/alma/config/environ"
. ${alma_environ}  # include environment file
# export all of the environ variables to my children
for env_var in $(cat ${alma_environ} | awk -F'=' '{print $1}')
do
  export ${env_var}
done

bin_dir="/alma/bin/"
config="/alma/config/produce_deleted_records.cfg"
config2="/alma/config/produce_withdrawn_records.cfg"
config_dir="/alma/config/"
error_log="/alma/integrations/oclc/delete/log/delete_oclc_log.$$"
error_log2="/alma/integrations/oclc/delete/log/delete_oclc_log2.$$"
log_parsed="/alma/integrations/oclc/delete/work/delete_oclc_log.txt"
log_parsed2="/alma/integrations/oclc/delete/work/delete_oclc_log2.txt"
results1="i/alma/integrations/oclc/delete/work/delete_oclc_results1.txt"
results2="/alma/integrations/oclc/delete/work/delete_oclc_results2.txt"
oclc_api_log="/alma/integrations/oclc/delete/log/oclc_api_$$"
#mail_list="acoope5@emory.edu egrant7@emory.edu"
mail_list="acoope5@emory.edu bgomez@emory.edu"
dow=$(date +%u)

####unset holdings for deleted titles
${bin_dir}get_alma_deleted_holdings.py ${config} 2> ${error_log} | ${bindir}oclc_delete_holdings.py ${config_dir}delete_oclc_holdings.cfg 2> ${oclc_api_log}
cat ${error_log} | grep exists >> ${log_parsed}
if [ -s ${log_parsed} ]; then
    if [ ${dow} == 1 ]; then
        mutt -a ${log_parsed} -s "Delete OCLC Holdings Report" -- ${mail_list} <<EOM
attached is today's log for deleted.
EOM

        rm ${log_parsed}
    fi

fi

####unset holdings for withdrawn titles
${bin_dir}get_alma_deleted_holdings.py ${config2} 2> ${error_log2} | ${bindir}oclc_delete_holdings.py ${config_dir}delete_oclc_holdings.cfg 2>> ${oclc_api_log}
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
