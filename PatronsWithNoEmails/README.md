#Patrons Without Emails
####python version 2.7.5

####bash version 4.1.2(1)

####Purpose: Produce a report of patron records in Alma that do not have an email or an invalid email

####Dependencies: the api scripts are using the socks and socket modules to place api calls via bela ; requires an Alma Analytics report

------------------------------------------

###master script to run the newly acquired scripts below
added to crontab
>06 08 * * 1 bash /alma/bin/patrons_no_email.sh 2> /tmp/patrons_no_email.log

-----------------------------------------

###get new records with analytics api

input = config file with:
```
url=https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports
path=[path of the analytics report]
apikey=[your api key]
limit=1000
```
> ${bindir}patrons_no_email_api.py ${config} > ${output} 2> ${errorlog}

output = csv report

---------------------------------------

###create analytics analysis

PatronsNoEmail.sql contains the sql of the query for the analysis

---------------------------------------
