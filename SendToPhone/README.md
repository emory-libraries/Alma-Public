**sendtophone** is a webservice that allows a user to 
send information about an item found on a discovery platform
like Primo.
**sendtophone** receives a list of one or more ALMA mms_ids and
it presents a list of elegible items. The user selects one item
and the **sendtophone_individual** webservice captures item information
from ALMA ( title, callnumber, holding library) and presents a webform
to the user requesting the mobile phone number and the carrier's name.
**sendtophone_individual** builds an SMS text message with the item 
information.

## Files ##
  - sendtophone.py ,
  - sendtophone_individual.py ,
  - sendtophone.cfg , 
  - sendtophone_individual.cfg ,
  - sendtophone_newcarrier.cfg
  - sendtophone.html ,
  - sendtophone_individual_input.html ,
  - sendtophone_individual_result.html ,
  - sendtophone_newcarrier.html ,
  - sendtophone_result_newcarrier.html ,
  - sendtophone_individual_failure.html 
