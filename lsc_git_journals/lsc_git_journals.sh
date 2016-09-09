#!/bin/bash
#Author: Alex
#Purpose: Get journal volumes owned by Georgia Tech in the LSC

#lsc_journals_analytics_api.py ../config/produce_lsc_journals.cfg 
config="/alma/config/produce_lsc_journals.cfg"
bin_dir="/alma/bin/"
script=${bin_dir}lsc_journals_analytics_api.py
target="/alma/integrations/lsc/git/journals/volumes"
today=$(date +"%Y%m%d")
header="ISSN|Material Type|MMSId|Title|Normalized Call Number|Call Number|Library|Location|Description|OCLC Number"

echo ${header} > ${target}${today}.txt
${script} ${config} >> ${target}${today}.txt

exit 0
