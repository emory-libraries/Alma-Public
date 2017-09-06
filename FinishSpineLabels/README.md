***finish_spine_process*** is a webservice that provides a form
to receive a text file with item barcodes and one or more email 
addresses. 
the webservice removes the two ALMA work orders linked to a given
barcode and it emails the results the designated email address(es).
to remove a work order, the webservice invokes the SCAN API operation.
the result file is in spreadsheet format.
the barcodes correspond to items that received spine labels from SpineOMatic, 
the Windows library application.

### Files:
- finish_spine_labels.cfg
- finish_spine_labels.py
- finish_spine_labels.sh
