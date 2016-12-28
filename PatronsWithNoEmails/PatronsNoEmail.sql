SELECT
   0 s_0,
   "Fulfillment"."Borrower Details"."Expiry Date" s_1,
   "Fulfillment"."Borrower Details"."First Name" s_2,
   "Fulfillment"."Borrower Details"."Last Name" s_3,
   "Fulfillment"."Borrower Details"."Primary Identifier" s_4,
   "Fulfillment"."Borrower Details"."Status Date" s_5,
   "Fulfillment"."Borrower Details"."User Group" s_6,
   "Fulfillment"."Preferred Contact Information"."Preferred Email" s_7
FROM "Fulfillment"
WHERE
(("Borrower Details"."User Group" NOT IN ('API', 'ILL-Proxy', 'Library Use')) AND (("Preferred Contact Information"."Preferred Email" IS NULL) OR ("Preferred Contact Information"."Preferred Email" NOT LIKE '%@%')))
ORDER BY 1, 5 ASC NULLS FIRST, 8 ASC NULLS FIRST, 7 ASC NULLS FIRST, 3 ASC NULLS FIRST, 4 ASC NULLS FIRST, 6 ASC NULLS FIRST, 2 ASC NULLS FIRST
FETCH FIRST 500001 ROWS ONLY
