#!/opt/rh/python27/root/usr/bin/python
r"""
Author: Alex C.
Date: 06/11/2019
Title: Filter MARC File
Required files: emory_bib_maintenance.d and 
/alma/integrations/backstage/work/extra_alma_keys.temp
"""
import sys
from pymarc import MARCReader

def filter_file(reader,target):
    for record in reader:
        mmsId = record['001'].value()
        if mmsId not in open(sys.argv[2]).read():
            target.write(record.as_marc())
        else:
            sys.stderr.write("MMSId " + mmsId + " is a duplicate!" + "\n")

def main():

    if len(sys.argv) < 2:
        sys.stderr.write("Expected 2 args: extra_alma_keys.temp and emory_bib_maintenance.d" + "\n")
        sys.exit(1)
    marcFile = open(sys.argv[1], 'rb')
    target = open('/tmp/my_marc.mrc', 'ab')
    reader = MARCReader(marcFile)
    filter_file(reader,target)

if __name__=="__main__":
    sys.exit(main())
