#Get GIT LSC Journals Holdings
####python version 2.7.5
####bash version 4.1.2(1)
####Purpose: Retrieve GIT journals holdings in the LSC for deduping
####Dependencies: GIT analytics is used to produce the list
---------------------------------------------------------------
###master script to run the script(s) below

added to crontab

>18 09 * * * bash /alma/bin/lsc_git_journals.sh 2> /tmp/lsc_git_journals.log

---------------------------------------------------------------
###get GIT journals holdings


input = config file with:

```
url=https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports
path=[path of the analytics report]
apikey=[your apikey]
limit=1000
```

>${bindir}lsc_journals_analytics_api.py ${config}

-------------------------------------------------------------------
###analytics report

query:

```
SELECT
   0 s_0,
   "Physical Items"."Bibliographic Details"."ISSN" s_1,
   "Physical Items"."Bibliographic Details"."Material Type" s_2,
   "Physical Items"."Bibliographic Details"."MMS Id" s_3,
   "Physical Items"."Bibliographic Details"."Title" s_4,
   "Physical Items"."Holding Details"."Normalized Call Number" s_5,
   "Physical Items"."Holding Details"."Permanent Call Number" s_6,
   "Physical Items"."Location"."Library Code" s_7,
   "Physical Items"."Location"."Location Code" s_8,
   "Physical Items"."Physical Item Details"."Description" s_9,
   CASE WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%OCOLC%'
THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('(OCOLC',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('(OCOLC',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','')
WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%OCM%'
THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('OCM',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('OCM',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','')
WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%OCN%'
THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','')
WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%ON%'
THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','')
ELSE 'No OCLC Number Available' END s_10
FROM "Physical Items"
WHERE
(("Location"."Library Code" = 'LSC') AND ("Bibliographic Details"."Material Type" = 'Journal'))
ORDER BY 1, 8 ASC NULLS FIRST, 9 ASC NULLS FIRST, 4 ASC NULLS FIRST, 2 ASC NULLS FIRST, 11 ASC NULLS FIRST, 5 ASC NULLS FIRST, 3 ASC NULLS FIRST, 6 ASC NULLS FIRST, 7 ASC NULLS FIRST, 10 ASC NULLS FIRST
FETCH FIRST 250001 ROWS ONLY
```

-------------------------------------------------------------------------------------------------
