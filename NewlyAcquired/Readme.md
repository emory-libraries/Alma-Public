#Newly Acquired Titles
####python version 2.7.5

####bash version 4.1.2(1)

####Purpose: Flag items acquired in the last 60 days to create a Newly Acquired flag for Primo

####Dependencies: this will also remove outdated ebooks ; analytics provides the list of records

-------------------------------------------------------------------------------------------------

###master script to run the newly acquired scripts below
added to crontab
>26 11 * * * bash /alma/bin/newly_acquired.sh 2> /tmp/newly_acquired.log

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
>${bindir}new_items_analytics_list.py ${config} > ${work}work_file_${todays_date} 2> $errorlog1

---------------------------------------------------------------------------------------------------

###modify the api results to a custom xml
input = file of pipe delimited item report

output = custom xml of item report
>cat ${work}work_file_${todays_date} | ${bindir}new_items_create_xml.py > ${work}work_file_parsed_${todays_date} 2> $errorlog2

------------------------------------------------------------------------------------------------------------------------------

###create a list of new and pending items
input = custom xml of item report

output = pipe delimited file of new and pending items
>cat ${work}work_file_parsed_${todays_date} | ${bindir}new_and_pending.py > ${work}new_mms_ids_${todays_date} 2> $errorlog3

--------------------------------------------------------------------------------------------------------------------------

###create 2 files: new and pending
input: pipe delimited file of new and pending items

output: files of new and pending items
>${bindir}new_and_pending.sh ${work}new_mms_ids_${todays_date} 2> ${errorlog4}

-------------------------------------------------------------------------------

###check pending file against alma
input = file of pending items, api key

output = file of items that are no longer pending
>cat ${pending} | ${bindir}new_check_pending.py ${api_key} > ${work}new_pending_${todays_date} 2> ${errorlog5}

-------------------------------------------------------------------------------------------------------------

###add no longer pending items to today's new list
>${bindir}new_pending_items_process.sh

------------------------------------------------

###add 598 $$a to new items
input: file of new mmsids, config file with api key
>cat ${new_titles}new_mms_ids_${todays_date} | ${bindir}new_items_put.py ${config2} 2> ${errorlog6}

--------------------------------------------------------------------------------------------------

###find file of old items and remove 598 $$a
this script runs old_items_update.py
>${bindir}old_items.sh 2> ${errorlog7}

--------------------------------------------------------------------------------------------------

###analytics report
Physical Items Analysis Bibliographic Details > MMS Id / Item Creation Date > Item Creation Date / Item Modification Date > Item Modification Date / Physical Item Details > Barcode / Physical Item Details > Process Type / Physical Item Details > Receiving Date

```
SELECT
   0 s_0,
   "Physical Items"."Bibliographic Details"."MMS Id" s_1,
   "Physical Items"."Item Creation Date"."Item Creation Date" s_2,
   "Physical Items"."Item Modification Date"."Item Modification Date" s_3,
   "Physical Items"."Physical Item Details"."Barcode" s_4,
   "Physical Items"."Physical Item Details"."Process Type" s_5,
   "Physical Items"."Physical Item Details"."Receiving   Date" s_6
FROM "Physical Items"
WHERE
("Item Creation Date"."Item Creation Date" >= (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE)))
ORDER BY 1, 2 ASC NULLS FIRST, 3 ASC NULLS FIRST, 4 ASC NULLS FIRST, 5 ASC NULLS FIRST, 6 ASC NULLS FIRST, 7 ASC NULLS FIRST
FETCH FIRST 250001 ROWS ONLY
```

Create a second Physical Items Analysis a Bibliographic Details > MMS Id / Item Creation Date > Item Creation Date / Item Modification Date > Item Modification Date / Physical Item Details > Barcode / Physical Item Details > Process Type / Physical Item Details > Receiving Date / Holding Details > Holding ID / Physical Item Details > Item ID 

```
SELECT
   0 s_0,
   "Physical Items"."Bibliographic Details"."MMS Id" s_1,
   "Physical Items"."Holding Details"."Holding Id" s_2,
   "Physical Items"."Physical Item Details"."Barcode" s_3,
   "Physical Items"."Physical Item Details"."Creation Date" s_4,
   "Physical Items"."Physical Item Details"."Item Id" s_5,
   "Physical Items"."Physical Item Details"."Modification Date" s_6,
   "Physical Items"."Physical Item Details"."Process Type" s_7,
   "Physical Items"."Physical Item Details"."Receiving   Date" s_8
FROM "Physical Items"
WHERE
("Bibliographic Details"."MMS Id" IN (SELECT saw_0 FROM (SELECT "Bibliographic Details"."MMS Id" saw_0, "Item Creation Date"."Item Creation Date" saw_1, "Item Modification Date"."Item Modification Date" saw_2, "Physical Item Details"."Barcode" saw_3, "Physical Item Details"."Process Type" saw_4, "Physical Item Details"."Receiving   Date" saw_5 FROM "Physical Items" WHERE "Item Creation Date"."Item Creation Date" >= (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE))) nqw_1 ))
ORDER BY 1, 2 ASC NULLS FIRST, 5 ASC NULLS FIRST, 7 ASC NULLS FIRST, 4 ASC NULLS FIRST, 8 ASC NULLS FIRST, 9 ASC NULLS FIRST, 3 ASC NULLS FIRST, 6 ASC NULLS FIRST
FETCH FIRST 250001 ROWS ONLY
```

---------------------------------------------------------------------------------------------------
