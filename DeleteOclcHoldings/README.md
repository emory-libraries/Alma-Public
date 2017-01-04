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

###get Alma MMSIds and OCLC numbers API
#####Purpose: retrieve Alma MMSIds and OCLC number from Analytics report for Yesterday's deletes via an API call and check via a SRU call that the bib record is no longer in Alma by checking for the OCLC number
#####Dependencies: Relies on Analytics reports based on these queries [1_days_deleted.sql](https://github.com/Emory-LCS/Alma-Public/blob/master/DeleteOclcHoldings/1_days_deleted.sql), [WithdrawnMonographs1-CollectMMSIDs.sql](https://github.com/Emory-LCS/Alma-Public/blob/master/DeleteOclcHoldings/WithdrawnMonographs1-CollectMMSIDs.sql), [WithdrawnMonographs2-ExcludeNon-WDs.sql](https://github.com/Emory-LCS/Alma-Public/blob/master/DeleteOclcHoldings/WithdrawnMonographs2-ExcludeNon-WDs.sql), [WithdrawnMonographs3Final.spl](https://github.com/Emory-LCS/Alma-Public/blob/master/DeleteOclcHoldings/WithdrawnMonographs3Final.spl)

input = config file with:

```
url=https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports
path=[path of the analytics report]
apikey=[your apikey]
limit=1000
```

>${bindir}get_alma_deleted_holdings.py

------------------------------------------------------------
