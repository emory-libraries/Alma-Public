#YBP PromptCat Processing
####Author: Alex Cooper, Bernardo Gomez, James Bias
####python version 2.7.5
####bash version 4.1.2(1)
####Purpose: Retrieve flies of records from the vendor and remove all records that alrerady exist in Alma

----------------------------------

###master script to run the other ones
####dependencies: requires C programs called marc_to_txt and txt_to_marc

added to crontab

>48 11,20 * * * bash /alma/bin/ybp_firm_receive.sh 2> /tmp/ybp_firm_receive.log

-----------------------------------

###get vendor records
####purpose: automate ftp retrieval of vendor provided files of MARC records (which have not been documented yet)

input:

```
data_file=${account_number}${today_date}.mrc
archivedir=/alma/integrations/vendors/ybp/univ/shelf_ready/archive
loginID=[id]
pass=[password]
gobi_directory=[gobi directory]
```

>${bindir}gobi.exp ${data_file} ${archivedir} ${loginID} ${pass} ${gobi_directory} 2>> ${expect_err}

output:

```
${expect_err}
${archivedir}/${data_file}
```

-------------------------------------

###check for duplicates
####purpose: use oclc numbers to check for pre-existing records from the vendor file in Alma and split the file into files of unique and duplicate records

input = file of marc records in plain text format

>${bindir}check_oclcno_via_sru.py

output = /tmp/ybp_sr_univ_duplicates.txt

----------------------------------------
