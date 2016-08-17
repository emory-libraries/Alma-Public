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

>${bindir}new_items_analytics_list.py ${config} > ${work}work_file_${todays_date} 2> $errorlog1

-------------------------------------------------------------------------------------------------
