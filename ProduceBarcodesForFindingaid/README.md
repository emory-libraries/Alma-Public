**produce_barcode_archives** is a webservice that receives 
  - a code belonging to a finding aid call number,
  - a finding aid call number type,
  - a Rose library repository name

and returns a list of barcodes associated with the
call number.
**produce_barcode_archives** searches Primo to get
titles whose callnumber contains the finding aid
code and belong to an "archives" resource type.
The mms_ids of the titles found in Primo are used to find the
barcodes in ALMA.
### Files:
 - produce_barcode_archives.py
 - produce_barcode_archives.cfg
 
