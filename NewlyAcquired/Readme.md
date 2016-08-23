#Newly Acquired Titles
####python version 2.7.5

####bash version 4.1.2(1)

####Purpose: Flag items acquired in the last 60 days to create a Newly Acquired flag for Primo

####Dependencies: this will also remove outdated ebooks ; analytics provides the list of records

-------------------------------------------------------------------------------------------------

#####master script to run the newly acquired scripts below
added to crontab
>26 11 * * * bash /alma/bin/newly_acquired.sh 2> /tmp/newly_acquired.log

-------------------------------------------------------------------------------------------------

#####get new records with analytics api
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

#####modify the api results to a custom xml
input = file of pipe delimited item report

output = custom xml of item report
>cat ${work}work_file_${todays_date} | ${bindir}new_items_create_xml.py > ${work}work_file_parsed_${todays_date} 2> $errorlog2

------------------------------------------------------------------------------------------------------------------------------

#####create a list of new and pending items
input = custom xml of item report

output = pipe delimited file of new and pending items
>cat ${work}work_file_parsed_${todays_date} | ${bindir}new_and_pending.py > ${work}new_mms_ids_${todays_date} 2> $errorlog3

--------------------------------------------------------------------------------------------------------------------------

#####create 2 files: new and pending
input: pipe delimited file of new and pending items

output: files of new and pending items
>${bindir}new_and_pending.sh ${work}new_mms_ids_${todays_date} 2> ${errorlog4}

-------------------------------------------------------------------------------

#####check pending file against alma
input = file of pending items, api key

output = file of items that are no longer pending
>cat ${pending} | ${bindir}new_check_pending.py ${api_key} > ${work}new_pending_${todays_date} 2> ${errorlog5}

-------------------------------------------------------------------------------------------------------------

#####add no longer pending items to today's new list
>${bindir}new_pending_items_process.sh

------------------------------------------------

#####add 598 $$a to new items
input: file of new mmsids, config file with api key
>cat ${new_titles}new_mms_ids_${todays_date} | ${bindir}new_items_put.py ${config2} 2> ${errorlog6}

--------------------------------------------------------------------------------------------------

#####find file of old items and remove 598 $$a
this script runs old_items_update.py
>${bindir}old_items.sh 2> ${errorlog7}
--------------------------------------------------------------------------------------------------

#####analytics report
Physical Items Analysis Bibliographic Details > MMS Id / Item Creation Date > Item Creation Date / Item Modification Date > Item Modification Date / Physical Item Details > Barcode / Physical Item Details > Process Type / Physical Item Details > Receiving Date

Filter: On Item Creation Date is greater tha or equal to add SQL expression
```
TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE)
```

Create a second Physical Items Analysis a Bibliographic Details > MMS Id / Item Creation Date > Item Creation Date / Item Modification Date > Item Modification Date / Physical Item Details > Barcode / Physical Item Details > Process Type / Physical Item Details > Receiving Date / Holding Details > Holding ID / Physical Item Details > Item ID

Filter: On MMS Id is based on the result of another analysis / saved analysis file location of first analysis / relationship is equal to any / use values in column MMS Id
---------------------------------------------------------------------------------------------------
