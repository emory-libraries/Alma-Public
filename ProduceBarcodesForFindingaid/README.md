**produce_barcode_archives** is a webservice that receives a
code belonging to a finding aid record, the name of a Rose library
repository; searches primo for the callnumber that matches the code;
and gets the barcodes in ALMA that are associated with the callnumber
and the repository.
**produce_barcode_archives** presents the list of barcodes as an XML object.

The search in primo is via a PNX deep link. The PNX response is
a JSON object that has the ALMA mms_id.

### Files:
 - produce_barcode_archives.py
 - produce_barcode_archives.cfg
 
