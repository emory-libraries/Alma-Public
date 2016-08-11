#!/bin/bash
#Author: Alex Cooper

input=$1
todays_date=(`date +"%Y%m%d"`)
new_books="/alma/integrations/new_books/primo/new_titles/new_mms_ids"
cached="/alma/integrations/new_books/primo/cache/new_cached"
pending="/alma/integrations/new_books/primo/pending/in_process_books"
cat ${input}|\
while read line; do
    array=(`echo $line | sed 's/|/\n/g'`)
    mms_id=(`echo ${array[0]}`)
    state=(`echo "${array[1]}${array[2]}"`)
    barcode=(`echo "${array[3]}"`)
    holding_id=(`echo "${array[4]}"`)
    item_id=(`echo "${array[5]}"`)
    if [ $state == "NEW" ]; then
        if cat ${cached} | grep ${mms_id}; then
            echo "${mms_id} is alread in the cache"
        else
            echo $mms_id >> ${new_books}_${todays_date}
            echo $mms_id >> $cached
        fi
    elif [ $state == "InProcess" ]; then
        if cat ${pending} | grep ${mms_id}; then
            echo "${mms_id} is already in pending file"
        elif cat ${cached} | grep ${mms_id}; then
            echo "${mms_id} is alread in the cache"
        else
            echo "${mms_id}|${holding_id}|${item_id}|" >> ${pending}
        fi
    else
        echo "no state"
    fi
done

exit 0
