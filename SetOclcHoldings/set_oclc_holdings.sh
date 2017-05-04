#!/bin/bash

alma_environ="/alma/config/environ"
. ${alma_environ}  # include environment file
# export all of the environ variables to my children
for env_var in $(cat ${alma_environ} | awk -F'=' '{print $1}')
do
  export ${env_var}
done

bin_dir="/alma/bin/"
config3="/alma/config/produce_set_list.cfg"
config_dir="/alma/config/"
error_log="/alma/integrations/oclc/delete/log/set_oclc_log.$$"
log_parsed1="/alma/integrations/oclc/delete/work/set_oclc_created.txt"
log_parsed2="/alma/integrations/oclc/delete/work/set_oclc_conflict.txt"
results="/alma/integrations/oclc/delete/work/set_oclc_results_$$.txt"
oclc_api_log="/alma/integrations/oclc/delete/log/oclc_api_$$"
#mail_list="acoope5@emory.edu,egrant7@emory.edu"
mail_list="acoope5@emory.edu"
#mail_list="acoope5@emory.edu,bgomez@emory.edu,DQM-L@LISTSERV.CC.EMORY.EDU"
dow=$(date +%u)

####unset holdings for deleted titles
${bin_dir}get_alma_set_holdings.py ${config} 2> ${error_log} | ${bindir}oclc_set_holdings.py ${config_dir}set_oclc_holdings.cfg > ${results} 2> ${oclc_api_log}
cat ${results} | grep Created >> ${log_parsed1}
cat ${results} | grep Conflict >> ${log_parsed2}
if [ -s ${log_parsed1} ]; then
####    if [ ${dow} == 1 ]; then
        mutt -a ${log_parsed1} -s "OCLC Holdings Created" -- ${mail_list} <<EOM
These OCLC holdings were updated.
EOM

        rm ${log_parsed1}
####    fi

if [ -s ${log_parsed2} ]; then
####    if [ ${dow} == 1 ]; then
        mutt -a ${log_parsed2} -s "OCLC Holdings Exist" -- ${mail_list} <<EOM
These OCLC records already had holings.
EOM

        rm ${log_parsed2}
####    fi


fi


exit 0
