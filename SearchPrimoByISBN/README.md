**search_by_isbn** is a webservice that receives a list of ISBNs and
an email address. It searches the ISBN in Primo to assert whether the
ISBN is part of Emory Libraries collection and it sends the results
to the designated email address(es).
If the ISBN is present in Primo, the result contains the Primo 
permalink of the title. If the ISBN is absent in Primo, the result
shows the link to Worldcat.

**search_by_isbn** uses a PNX deep link to perform the ISBN search.

### Files:
 - search_isbn.py
 - search_isbn.cfg
 - search_isbn.sh
 
