#Delete OCLC Holdings
####python version 2.7.5
####bash version 4.1.2(1)
####Purpose: Delete OCLC holdings for deleted and withdrawn bibliographic records
####Dependencies: titles that have been deleted or withdrawn will have their OCLC holdings removed ; analytics is used to produce the list of OCLC numbers ; sru is used to ensure that there are no duplicate holdings in Alma
-----------------------------------------------------

###master script to run the script(s) below

added to crontab

>06 09 * * * bash /alma/bin/delete_oclc_holdings.sh 2> /tmp/delete_oclc_holdings.log

-------------------------------------------------------

