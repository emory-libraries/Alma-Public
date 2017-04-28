SELECT
   0 s_0,
   "Physical Items"."Bibliographic Details"."Local Param 1" s_1,
   "Physical Items"."Bibliographic Details"."Material Type" s_2,
   "Physical Items"."Bibliographic Details"."MMS Id" s_3,
   "Physical Items"."Library Unit"."Library Name" s_4,
   "Physical Items"."Location"."Location Code" s_5,
   "Physical Items"."Physical Item Details"."Barcode" s_6,
   "Physical Items"."Physical Item Details"."Creation Date" s_7,
   "Physical Items"."Physical Item Details"."Lifecycle" s_8,
   "Physical Items"."Physical Item Details"."Modification Date" s_9,
   "Physical Items"."Physical Item Details"."Process Type" s_10,
   CASE WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%OCOLC%' THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('(OCOLC',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('(OCOLC',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','') WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%OCM%' THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('OCM',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('OCM',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','') WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%OCN%' THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','') WHEN UPPER("Physical Items"."Bibliographic Details"."Network Number") LIKE '%ON%' THEN REPLACE(LEFT(SUBSTRING("Physical Items"."Bibliographic Details"."Network Number" FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))),LOCATE(' ',SUBSTRING(CONCAT("Physical Items"."Bibliographic Details"."Network Number",'; ') FROM LOCATE('OCN',UPPER("Physical Items"."Bibliographic Details"."Network Number"))))),';','') ELSE 'No OCLC Number Available' END s_11
FROM "Physical Items"
WHERE
(("Physical Item Details"."Barcode" NOT LIKE '%EMU%') AND ("Location"."Location Code" = 'STACK') AND ("Library Unit"."Library Name" = 'Robert W. Woodruff Library') AND ((("Bibliographic Details"."Local Param 1" NOT LIKE '%PROMPTCAT%') AND ("Bibliographic Details"."Local Param 1" NOT LIKE '%YBPAPP%')) OR ("Bibliographic Details"."Local Param 1" IS NULL)) AND ("Physical Item Details"."Lifecycle" = 'Active') AND ("Bibliographic Details"."Material Type" <> 'Journal') AND ((("Physical Item Details"."Creation Date" IN (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE)))) OR (("Physical Item Details"."Modification Date" IN (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE))))) AND ("Physical Item Details"."Process Type" = 'None') AND ("Physical Item Details"."Barcode" NOT IN (SELECT saw_0 FROM (SELECT "Physical Item Details"."Barcode" saw_0 FROM "Fulfillment" WHERE (("Return Date"."Return Date" >= (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE))) OR ("Loan Date"."Loan Date" >= (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE)))) AND ("Physical Item Details"."Process Type" = 'None')) nqw_1 )))
