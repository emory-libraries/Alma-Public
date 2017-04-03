#!/bin/bash

setfile="/tmp/setids"
bindir="/sirsi/webserver/bin/"
config="/sirsi/webserver/config/alma_delete_set_api.cfg"

cat ${setfile} |\
while read line; do
    echo ${line} | ${bindir}delete_alma_set_api.py ${config} > "/tmp/delete_set_$$.log" 2> "/tmp/delete_set_$$.err"
done

exit 0
