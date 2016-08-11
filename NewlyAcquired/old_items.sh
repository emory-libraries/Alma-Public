#!/bin/bash

#sixty_days=$(date +"%Y%m%d" -d"1 day ago")
sixty_days=$(date +"%Y%m%d" -d"60 days ago")
bindir="/alma/bin/"
targetdir="/alma/integrations/new_books/primo/new_titles/"

find ${targetdir} -type f | while read file; do
    file_date=$(echo ${file} | sed 's/^.*[^0-9]//')
    if [ ${file_date} -lt ${sixty_days} ]; then
        cat ${file}|\
        while read line; do
            echo ${line} | ${bindir}old_items_update.py ${api_key}
        done
        rm ${file}
    fi
done

exit 0
