#!/bin/bash

today=$(date +"%Y%m%d")
sixty_days=$(date +"%Y%m%d" -d"60 days ago")
bindir="/alma/bin/"
mail_list="acoope5@emory.edu"
targetdir="/alma/integrations/new_books/primo/new_titles/"
cache="/alma/integrations/new_books/primo/cache/new_cached"
config="/alma/config/produce_new_ebooks.cfg"
errorlog1="/tmp/new_act_err1_$$.log"
errorlog2="/tmp/new_act_err2_$$.log"

${bindir}new_ebooks_api.py ${config} > ${targetdir}new_ebooks_${today} 2> ${errorlog1}
if [ -f ${targetdir}new_ebooks_${today} ]; then
    if [ -s ${targetdir}new_ebooks_${today} ]; then
        cat ${targetdir}new_ebooks_${today}|\
        while read line; do
            if cat ${cache} | grep ${line}; then
                echo "${line} is already in cache"
            else
                echo ${line} | ${bindir}new_items_put.py ${config} 2> ${errorlog2}
                echo ${line} >> ${cache}
            fi
        done
    else
        mutt -s ${targetdir}new_ebooks_${today} -- ${mail_list} <<EOM
File ${targetdir}new_ebooks_${today} was not created today.
EOM
    fi
fi

exit 0
