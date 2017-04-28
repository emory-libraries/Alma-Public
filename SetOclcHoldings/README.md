# Under Construction!!!
#### Contributers: Alex Cooper, Bernardo Gomez, Erin Grant, Lisa Hamlett
#### python version 2.7.5
#### bash version 4.1.2(1)
#### Purpose: Set OCLC holdings for deleted and withdrawn bibliographic records
#### Dependencies: titles that have been newly added will have their OCLC holdings set ; analytics is used to produce the list of OCLC numbers
-----------------------------------------------------

### master script to run the script(s) below

added to crontab

>06 09 * * * bash /alma/bin/set_oclc_holdings.sh 2> /tmp/set_oclc_holdings.log

-------------------------------------------------------

### get OCLC numbers API
##### Purpose: retrieve OCLC number from Analytics report for Yesterday's deletes via an API call and check via a SRU call that the bib record is no longer in Alma by checking for the OCLC number
##### Dependencies: Relies on Analytics reports based on these queries [SetOCLCHolTESTexclFULFILL.sql](https://github.com/Emory-LCS/Alma-Public/blob/master/SetOclcHoldings/SetOCLCHolTESTexclFULFILL.sql), [SetOCLCHolTEST.sql](https://github.com/Emory-LCS/Alma-Public/blob/master/SetOclcHoldings/SetOCLCHolTEST.sql)

input = config file with:

```
url=https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports
path=[path of the analytics report]
apikey=[your apikey]
limit=1000
```

output = OCLC numbers for holding to be set

>${bindir}get_alma_set_holdings.py ${config}

------------------------------------------------------------

### set OCLC holdings

input = list of OCLC numbers + config file with:

```
url=https://worldcat.org/ih/
clientId=[your client id]
secret=[your secret key]
http_method=POST
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

>${bindir}oclc_set_holdings.py ${config}

-------------------------------------------------
