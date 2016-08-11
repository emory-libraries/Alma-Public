#!/bin/bash
#Author: Alex C.
#Purpose: Clean pending file
#/alma/integrations/new_books/primo/pending/in_process_books

input="/alma/integrations/new_books/primo/pending/in_process_books"
bindir="/alma/bin/"
processing="${bindir}new_check_pending.py"
newdir="/alma/integrations/new_books/primo/new_titles/"
workdir="/alma/integrations/new_books/primo/work/"
todays_date=(`date +"%Y%m%d"`)
new_file="${newdir}new_mms_ids_${todays_date}"
work_file="${workdir}new_pending_${todays_date}"
#input="/tmp/items_test"
#work_file="/tmp/mmsid"

cat ${work_file}|\
while read line; do
    mms_id=${line}
    echo ${mms_id} >> ${new_file}
    sed -i '/^'${mms_id}'/d' ${input}
done
#rm ${work_file}

exit 0
