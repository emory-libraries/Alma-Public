**marc_to_txt** is a C program that reads a MARC file
on the standard input and writes a text file to standard output.
The text file has the following format:
```
******
000||leader
001||control field
010|indicators|\pasubfielda\pbsubfieldb
```

the leader is given the "000" tag;
001-009 are control fields and they don't have
indicators;
010-999 are datafields are they have indicators;
"\p" is the subfield separator.

### Files:
 - makefile ( it builds the C binary)
 - MARC_subs.c
 - marc_to_txt.c 
 - e_marc.h
 
 To build **marc_to_txt** , issue the following command
 ```
  make marc_to_txt
 ```
