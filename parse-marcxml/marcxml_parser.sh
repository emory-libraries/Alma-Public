#!/bin/bash
dir="/alma/integrations/tmp/"
files="/alma/integrations/tmp/ustorgd"
#files="/alma/integrations/tmp/ustorgd_2018071918_16394506000002486_new_1.xml.tar.gz"
script="/alma/bin/marcxml_parser.py"
target="/tmp/steves_report.txt"
cd ${dir}
for f in ${files}*; do
    echo "Untaring ${f}"
    tar -xf ${f}
    nfile=$(basename ${f} .tar.gz)
    echo "Changing permission for ${nfile}"
    chmod 644 ${nfile}
    echo "Processing ${nfile}"
    cat ${nfile} | ${script} >> ${target}
    echo "Result can be found in ${target}"
done

exit 0
