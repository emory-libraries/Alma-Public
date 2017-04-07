#!/bin/bash

config="/sirsi/webserver/config/"
. ${config}environ     # dot in environ variables

# export all of the environ variables to my children
for env_var in $(cat ${config}environ | awk -F'=' '{print $1}')
do
  export ${env_var}
done

direc="/sirsi/webserver/external_data/set_management/barcodes/"
archive="/sirsi/webserver/external_data/set_management/barcodes/archive/"
workdir="/sirsi/webserver/external_data/set_management/barcodes/work/"
bindir="/sirsi/webserver/bin/"
configdir="/sirsi/webserver/config/"
delete_log="/tmp/delete_me_$$.log"
delete_err="/tmp/delete_me_$$.err"
process_log="/tmp/process_me_$$.log"
process_err="/tmp/process_me_$$.err"
####create sets and store ids
setid1=$(${bindir}create_alma_set_api.py ${configdir}alma_create_delete_set.cfg)
setid2=$(${bindir}create_alma_set_api.py ${configdir}alma_create_process_set.cfg)
setfile="/tmp/setids"
mail_list="acoope5@emory.edu"
today=$(date +"%Y%m%d")

####split barcode file into batches of 100
count=0
for f in ${direc}delete_me_*; do
    if [ ${count} -eq 0 ]; then
        split -l 100 -d ${f} ${workdir}deletes_
        mv ${f} ${archive}
        ((count++))
    elif [ ${count} -gt 0 ]; then
        break
    fi
done

####split barcode file into batches of 100
count=0
for f in ${direc}process_me_*; do
    if [ ${count} -eq 0 ]; then
        split -l 100 -d ${f} ${workdir}process_
        mv ${f} ${f}.${today}
        mv ${f}.${today} ${archive}
        ((count++))
    elif [ ${count} -gt 0 ]; then
        break
    fi    
done

####add members to delete set 100 at a time
if [ -e ${workdir}deletes_00 ]; then
    for f in ${workdir}deletes*; do
        cat ${f} | ${bindir}addto_alma_set_api.py ${configdir}alma_add_members_api.cfg ${setid1} > ${delete_log} 2>> ${delete_err}
        if [ -s ${delete_err} ]; then
            mail -a ${f} -s "An error occured in adding to the set" ${mail_list} <<EOM
While processing $(echo ${f}) the following error occurred:

$(cat ${delete_err})
EOM
            rm ${delete_err}
        else
            rm ${f}
        fi
    done
####check the number of barcodes added to the delete set
    number_of_members=$(echo ${setid1} | ${bindir}get_alma_set_api.py ${configdir}alma_get_set_api.cfg)
    if [ ${number_of_members} -lt 4500 ]; then
        mail -s "Delete Me File is Small" ${mail_list} <<EOM
        delete_me only has ${number_of_members} members.
EOM
    fi
####run the job to delete the items
    ${bindir}run_delete_job_api.py ${configdir}alma_run_delete_job.cfg ${setid1}
fi

####add members to publishing set 100 at a time
if [ -e ${workdir}process_00 ]; then
    for f in ${workdir}process*; do
        cat ${f} | ${bindir}addto_alma_set_api.py ${configdir}alma_add_members_api.cfg ${setid2} > ${process_log} 2>> ${process_err}
        if [ -s ${process_err} ]; then
            mail -a ${f} -s "An error occured in adding to the set" ${mail_list} <<EOM
While processing $(echo ${f}) the following error occurred:

$(cat ${process_err})
EOM
            rm ${process_err}
        else
            rm ${f}
        fi
        rm ${f}
    done
####check the number of barcodes added to the delete set
    number_of_members=$(echo ${setid2} | ${bindir}get_alma_set_api.py ${configdir}alma_get_set_api.cfg)
    if [ ${number_of_members} -lt 4500 ]; then
        mail -s "Process Me File is Small" ${mail_list} <<EOM
        process_me only has ${number_of_members} members.
EOM
    fi
fi

####create file with set ids for delete set script
echo ${setid1} > ${setfile}

echo ${setid2} >> ${setfile}

exit 0
