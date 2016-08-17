#New Ebooks
####python version 2.7.5
####bash version 4.1.2(1)
####Purpose: Flag items acquired in the last 60 days to create a Newly Acquired flag for Primo
####Dependencies: the api scripts are using the socks and socket modules to place api calls via bela
-------------------------------------------------------------------------------------------------
#####master script to run the newly acquired scripts below

added to crontab

>06 11 * * * bash /alma/bin/new_ebooks_process.sh 2> /tmp/new_ebooks.log

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

>${bindir}new_ebooks_api.py ${config} > ${work}work_file_${todays_date} 2> $errorlog1

-------------------------------------------------------------------------------------------------
#####add 598 $$a to new items
input: file of new mmsids, config file with apikey
>cat ${new_titles}new_mms_ids_${todays_date} | ${bindir}new_items_put.py ${api_key} 2> ${errorlog6}

-------------------------------------------------------------------------------------------------
