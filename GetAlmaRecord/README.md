***get_alma_record*** is a webservice that queries ALMA's API server to
retrieve a bibliographic record and its copies. The API server returns
XML strings and *get_alma_record* assembles the record in one of three
formats:
- xml (MARCXML ), 
- marcedit ( terry reese's marcEdit), 
- text (bernardo gomez plain-text format)

Example of webservice URL: 
- https://kleene.library.emory.edu/cgi-bin/get_alma_record?doc_id=9936579694202486&format=marcedit
- https://kleene.library.emory.edu/cgi-bin/get_alma_record?item_id=010002975279 

Default format is "xml".
### Files:
- get_alma_record.cfg
- get_alma_record.py


