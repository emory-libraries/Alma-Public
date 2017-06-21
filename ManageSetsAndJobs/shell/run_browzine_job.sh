#!/bin/bash

config="/sirsi/webserver/config/"
. ${config}environ     # dot in environ variables

# export all of the environ variables to my children
for env_var in $(cat ${config}environ | awk -F'=' '{print $1}')
do
  export ${env_var}
done

script="/sirsi/webserver/bin/run_browzine_job_api.py"
config="/sirsi/webserver/config/alma_run_browzine_job.cfg"
error="/tmp/browzine_err_$$.txt"

${script} ${config} 2> ${error}

exit 0
