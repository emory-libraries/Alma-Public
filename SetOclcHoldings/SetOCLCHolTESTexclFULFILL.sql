SELECT
   0 s_0,
   "Fulfillment"."Physical Item Details"."Barcode" s_1
FROM "Fulfillment"
WHERE
((("Return Date"."Return Date" >= (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE))) OR ("Loan Date"."Loan Date" >= (TIMESTAMPADD(SQL_TSI_DAY, -1, CURRENT_DATE)))) AND ("Physical Item Details"."Process Type" = 'None'))
