# Dedup Load Files
#### python version 2.7.5
#### Purpose: check oclc numbers in load files against alma to avoid duplication
#### Dependencies: requires a text file as produced from MARC using marc_to_txt
-------------------------------------------------------------------------------
### check_oclcno_via_sru.py
input = a marc.txt file

```
cat marc.txt | check_oclcno_via_sru.py > /alma/integrations/data/ybp/shelf_ready/out/${prefix}${account_number}${today_date}.mrc
```

output = 1 file of records to be loaded , 1 file of duplicate records

------------------------------------------------
