SELECT
   0 s_0,
   "Physical Items"."Bibliographic Details"."Bibliographic Life Cycle" s_1,
   "Physical Items"."Bibliographic Details"."Material Type" s_2,
   "Physical Items"."Bibliographic Details"."MMS Id" s_3,
   "Physical Items"."Bibliographic Details"."Modification Date" s_4,
   "Physical Items"."Bibliographic Details"."Network Number" s_5,
   "Physical Items"."Bibliographic Details"."Title" s_6,
   CASE WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%OCOLC%'
THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('(OCOLC',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('(OCOLC',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','')
WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%OCM%'
THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('OCM',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('OCM',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','')
WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%OCN%'
THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','')
WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%ON%'
THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','')
ELSE 'No OCLC Number Available' END s_7
FROM "Physical Items"
WHERE
(("Bibliographic Details"."Bibliographic Life Cycle" = 'Deleted') AND ("Bibliographic Details"."Modification Date" >= (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE))))
