#!/bin/bash
# Description: It reads email messages that contain the names
#
# Author: Bernardo Gomez.
# Creation date: March 2000
# 
#modified to run with Alma to notify library staff that a file is available for pickup   04-01-2016-agc

#check to see if the record is marc8
is_marc8 () {
unset tmarc8;
tmarc8=$(egrep '[0-9][0-9][0-9][0-9][0-9][acdnp][acdefgijkmoprt][abcdims][  a] ' $1) ;
if [ "$tmarc8" ]; then echo -n "true"; fi 
}

#check to see if the record is utf8
is_utf8 () {
unset tmarc8;
tutf8=$(egrep '[0-9][0-9][0-9][0-9][0-9][acdnp][acdefgijkmoprt][abcdims][  a]a' $1) ;
if [ "$tutf8" ]; then echo -n "true"; fi 
}



function parse_outcome_data {
	if [ $status -eq 0 ]
	then        
	              if [ "$(is_marc8 $archivedir/$data_file)" ]; then 
                        /usr/bin/yaz-marcdump -f MARC-8 -t UTF-8 -i marc -o marc -l 9=97  $archivedir/$data_file > $datadir/${file_prefix}_$target_file 2> $errors  ;
                        #echo "$? error code for yaz $errors ";
                      elif [ "$(is_utf8 $archivedir/$data_file)" ]; then 
                       	cp  $archivedir/$data_file  $datadir/${file_prefix}_$target_file 2> $errors ;
                       # echo "$? error code for cp $errors "; 
                      else  
                        #send email because $archivedir/$data_file is neither marc8 nor utf8
                        #echo "unkown text encoding";
                        mail -s "$0 on turing. GOBI Marc Record with unkown text encoding  $archivedir/$data_file" $mail_list <<EOM
file $archivedir/$data_file  has bad text encoding  on $(date +"%Y/%m/%d")
EOM
false;
                      fi

		    if [ $? -eq 0 ]; then

                    work_file_agc="/tmp/ybp_sr_univ_work_${today}"
                    mail_body="/tmp/univ_gobi_mail_body"
                    mail_body_02="/tmp/univ_gobi_mail_body_02"
                    work_file_02_agc="/tmp/ybp_sr_univ_work_02.txt"
                    work_file_03_agc="/tmp/ybp_unique_sr_univ.txt"
                    duplicates="/tmp/ybp_sr_univ_duplicates.txt"
                    duplicates_marc="${archivedir}/ybp_sr_univ_duplicates_${today}.mrc"
                    unique="${archivedir}/promptcatF_univ_${today}.mrc"
                    cat $datadir/${file_prefix}_$target_file | marc_to_txt > ${work_file_02_agc}
                    cat ${work_file_02_agc} | check_oclcno_via_sru.py > ${work_file_03_agc}
                    cat ${work_file_03_agc} | txt_to_marc > ${unique}
                    cat ${unique} | marc_to_txt -e 020,022,245 | sed 's/^020|  |/ISBN\: /' | sed 's/^245|.*|/Title: /' | sed 's/\\pa//' | sed 's/\\pb/ /' |sed 's/\\ph/ /' | sed 's/\\pc//'  > $mail_body
                    cat ${duplicates} | txt_to_marc > ${duplicates_marc}
                    cat ${duplicates_marc} | marc_to_txt -e 020,022,245 | sed 's/^020|  |/ISBN\: /' | sed 's/^245|.*|/Title: /' | sed 's/\\pa//' | sed 's/\\pb/ /' |sed 's/\\ph/ /' | sed 's/\\pc//'  > ${mail_body_02}
                    cat ${unique} | marc_to_txt | /alma/bin/promptcat.py --promptcat PROMPTCATF --library EMU > $work_file_agc

                    cat $work_file_agc | /alma/bin/marc_splitter.py --directory /tmp --prefix ${file_prefix}_${today}_$$ --size 50 

                    if [ -s ${duplicates_marc} ]; then
                        mutt -s "shelf-ready ${duplicates_marc}" -a ${duplicates_marc} -- ${mail_list} <<EOM
   marc file of duplicates is attached.

   With these titles:

$(cat ${mail_body_02})
EOM
                    else
                        mutt -s "shelf-ready without duplicates" -- ${mail_list} <<EOM
   No duplicates were found in today's files.
EOM
                    fi

                    for file in /tmp/$file_prefix*.txt; do
                        nfile=$(basename ${file} .txt)
                        cat $file | txt_to_marc > ${dataout}/${nfile}.mrc
                        mutt -s"shelf-ready ${nfile}.mrc" -a ${dataout}/${nfile}.mrc -- $katie_email <<EOM
   marc file is attached.
EOM
                        rm $file
                    done

                    if [ -s ${work_file_agc} ]; then
	            mail -s "$0 on turing. GOBI $data_file received OK" $mail_list <<EOM
$datadir/${file_prefix}_$target_file has been created on $(date +"%Y/%m/%d")

With these titles:

$(cat ${mail_body})
EOM
                    fi
			 touch  $tracking
			else
                mail -s "$0 on turing. Could not deposit GOBI file" $mail_list <<EOM
$datadir/${file_prefix}_$target_file was not  created on $(date +"%Y/%m/%d")
EOM


		outcome=$?
			chmod 664 $datadir/${file_prefix}_$target_file
		    rm -f  $errors 
		fi
	elif [ $status -eq 101 ]
	then
	 mail -s "$0 on turing. GOBI ftp failed - 101" $mail_list <<EOM
	File: $data_file . Reason: ftp server didn't respond.
	Action recommended: NONE. Will try again later.
EOM
	elif [ $status -eq 102 ]
	then
	 mail -s "$0 on turing. GOBI ftp failed - 102" $mail_list <<EOM
	File: $data_file. Reason: GOBI didn't accept login name.
	Action recommended: Revise gobi.exp 
EOM
	elif [ $status -eq 103 ]
	then
	 mail -s "$0 on turing. GOBI ftp failed - 103" $mail_list <<EOM
	File: $data_file . Reason: GOBI didn't accept password.
	Action recommended: Revise gobi.exp 
EOM
	elif [ $status -eq 104 ]
	then
	 mail -s "$0 on turing. GOBI ftp failed - 104" $mail_list <<EOM
	File: $data_file . Reason: Couldn't change to "orders" directory.
	Action recommended: Revise gobi.exp 
EOM
	elif [ $status -eq 105 ]
	then
	 mail -s "$0 on turing. GOBI ftp failed - 105" $mail_list <<EOM
	File: $data_file . Reason: Problem with bin command.
	Action recommended: Revise gobi.exp 
EOM
	elif [ $status -eq 106 ]; then
	 	operation=NONE	#no file this time.
	elif [ $status -eq 107 ]
	then
	 mail -s "$0 on turing. GOBI ftp failed - 107" $mail_list <<EOM
	File: $data_file . Reason: File didn't arrive.
	Action recommended: NONE. Will try again later. 
EOM
	elif [ $status -eq 108 ]
	then
	 mail -s "$0 on turing. GOBI ftp failed - 108" $mail_list <<EOM
	File: $count_file . Reason: directory or file must have wrong name.
	Action recommended: Revise GOBI scripts.
EOM
	else
	 mail -s "$0 on turing. GOBI ftp failed " $mail_list <<EOM
	File: $data_file . Reason: Problems with expect script.
	Action recommended: Review gobi.exp.
EOM
	fi
}

config="/alma/config/" 
. ${config}environ     # dot in environ variables

# export all of the environ variables to my children
for env_var in $(cat ${config}environ | awk -F'=' '{print $1}')
do
  export ${env_var}
done


###### begin global variables ######
exp_file=/alma/bin
expect_err=/tmp/genybpsr_exp1
loginID=[login] 
pass=[password]
mode=bin
errors=/tmp/gengobi.mail.error$$
archivedir=/alma/integrations/vendors/ybp/univ/shelf_ready/archive 
trackingdir=/alma/integrations/vendors/ybp/univ/shelf_ready/tracking
temp=/alma/integrations/vendors/ybp/univ/shelf_ready/work/
datadir="/alma/integrations/data/ybp/shelf_ready/in"
dataout="/alma/integrations/data/ybp/shelf_ready/out"
mail_list="[emails]"
katie_email="[emails]"
account_number="[account number]"
file_prefix="[file prefix]"
gobi_directory="[gobi directory]"
umask u+rw,g+rw,o+rw
today=$(date +%Y%m%d)
if [ $# -lt 1 ]; then
  count=8
else
  count=$1
fi

date_file=${temp}date_file_$$
while [ $count -gt 0 ]; do
   my_date=$(date +"%y%m%d" -d "${count} days ago")
   echo $my_date >> ${date_file}
   count=$(expr $count - 1)
done

####### main loop with enchilada follows here #####
if [ -s "${date_file}" ]; then
   cat "${date_file}" |\
   while read today_date;  do
     tracking="$trackingdir/${file_prefix}_${account_number}${today_date}.cnt"
     data_file=${account_number}${today_date}.mrc
     target_file=${account_number}${today_date}.mrc
     target_file=$(echo "${target_file}" | tr '[A-Z]' '[a-z]')
     if [ ! -f $tracking ]; then
	$exp_file/gobi.exp $data_file $archivedir $loginID $pass ${gobi_directory} 2>> $expect_err
	status=$?
	parse_outcome_data
     fi
   done
fi

exit 0
