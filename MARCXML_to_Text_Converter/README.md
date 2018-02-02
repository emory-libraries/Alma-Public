**marcxml_to_text.cpp** is the source code of a C++ program that reads a MARCXML file on the standard
input; translates the file to a text file and writes it to standard ouput.
an example of a text file:
```
*******
000||01130nam a2200349Ia 4500
001||990026432640302486
005||20160111232221.0
008||930726s19930000enka     b    001 0 eng  
020|  |\pa0334025338
020|  |\pa9780334025337
035|  |\pa(Aleph)002643264EMU01
035|9 |\pau930751
035|  |\paocm28357728
035|  |\pa(DOBI)32075544
040|  |\paDLM\pcDLM\pdEMU\pdUtOrBLW
043|  |\pae-uk-en
049|  |\paEMUU
090|  |\paHV8699.G8\pbP68 1993
100|1 |\paPotter, Harry.
245|10|\paHanging in judgement :\pbreligion and the death penalty in England from the bloody code to abolition /\pcHarry Potter.

``` 
the 000 tag is the record LEADER; ``` ***** ``` is a record delimiter.


***makefile_xml*** is the make file that produces the marcxml_to_text binary.

to produce **marcxml_to_text** :
- you must install the http://xerces.apache.org/xerces-c/ library. 
- you must add **/usr/local/lib** to  **LD_LIBRARY_PATH** environment.


