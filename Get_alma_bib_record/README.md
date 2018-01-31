**get_alma_bib** is a webservice that receives a list of one or more ALMA mms_ids, retrieves the ALMA bibliographic records in MARCXML
format and display the record in one of three formats: "xml", or "marcedit", or "text".
for instance, the webservice URL would look like https://kleene.library.emory.edu/cgi-bin/get_alma_bib?doc_id=990020504620302486,990018353460302486&format=marcedit

**files:**
 - get_alma_bib.cfg contains ALMA's API key and ALMA's API hostname.
 - get_alma_bib.py contains the CGI script that receives the two webservice
    parameters: "doc_id" and "format" ; retrieves the records from ALMA's API server;
    and composes the http outpout according to requested format.
    
