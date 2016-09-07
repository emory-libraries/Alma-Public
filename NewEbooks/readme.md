#New Ebooks
####python version 2.7.5
####bash version 4.1.2(1)
####Purpose: Flag items acquired in the last 60 days to create a Newly Acquired flag for Primo
####Dependencies: titles that are older than 60 days will be removed when the newly acquired script runs ; analytics is used to produce the list of record numbers
-------------------------------------------------------------------------------------------------
###master script to run the new ebooks scripts below

added to crontab

>06 11 * * * bash /alma/bin/new_ebooks_process.sh 2> /tmp/new_ebooks.log

-------------------------------------------------------------------------------------------------
###get new records with analytics api

input = config file with:

```
url=https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports

path=[path of the analytics report]

apikey=[your api key]

limit=1000
```

output = pipe delimited item report

>${bindir}new_ebooks_api.py ${config} > ${work}work_file_${todays_date} 2> $errorlog1

-------------------------------------------------------------------------------------------------
###add 598 $$a to new items
input: file of new mmsids, config file with apikey
>cat ${new_titles}new_mms_ids_${todays_date} | ${bindir}new_items_put.py ${api_key} 2> ${errorlog6}

-------------------------------------------------------------------------------------------------
###analytics report
EInventory Bibliographic Details > MMS Id / Portfolio Activation Date > Portfolio Activation Date

```
SELECT
   0 s_0,
   "E-Inventory"."Bibliographic Details"."MMS Id" s_1,
   "E-Inventory"."Portfolio Activation Date"."Portfolio Activation Date" s_2
FROM "E-Inventory"
WHERE
(("Portfolio Activation Date"."Portfolio Activation Date" IN (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE))))
ORDER BY 1, 2 ASC NULLS FIRST, 3 ASC NULLS FIRST
FETCH FIRST 250001 ROWS ONLY
```
-------------------------------------------------------------------------------------------------
