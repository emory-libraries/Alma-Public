#Delete OCLC Holdings
####Authors: Alex Cooper, Bernardo Gomez, Lisa Hamlet
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
#####Dependencies: Relies on Analytics reports based on these queries [1_days_deleted.sql](https://github.com/Emory-LCS/Alma-Public/blob/master/DeleteOclcHoldings/1_days_deleted.sql), [WithdrawnMonographs1-CollectMMSIDs.sql](https://github.com/Emory-LCS/Alma-Public/blob/master/DeleteOclcHoldings/WithdrawnMonographs1-CollectMMSIDs.sql), [WithdrawnMonographs2-ExcludeNon-WDs.sql](https://github.com/Emory-LCS/Alma-Public/blob/master/DeleteOclcHoldings/WithdrawnMonographs2-ExcludeNon-WDs.sql), [WithdrawnMonographs3Final.sql](https://github.com/Emory-LCS/Alma-Public/blob/master/DeleteOclcHoldings/WithdrawnMonographs3Final.sql)

input = config file with:

```
url=https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports
path=[path of the analytics report]
apikey=[your apikey]
limit=1000
```

output = OCLC numbers for holding to be removed and report of OCLC numbers that are still in Alma and need to be checked by staff

>${bindir}get_alma_deleted_holdings.py ${config}

------------------------------------------------------------

###remove OCLC holdings

input = list of OCLC numbers + config file with:

```
url=https://worldcat.org/ih/
clientId=[your client id]
secret=[your secret key]
http_method=DELETE
oclc_curl=www.oclc.org
port=443
path=wskey/
principalID=[your principal id]
principal_namespace=urn:oclc:wms:da
classification_scheme=LibraryOfCongress
institution_id=[your 3 digit institution id]
library_code=[your 4 character library code]
```

output = API response

>${bindir}oclc_delete_holdings.py ${config}

-------------------------------------------------
