CC = /usr/bin/gcc 
OPTIONS = -c -g

all: marc_to_txt

marc_to_txt: marc_to_txt.o MARC_subs.o
	$(CC) -o marc_to_txt marc_to_txt.o MARC_subs.o 
marc_to_txt.o: marc_to_txt.c
	$(CC) $(OPTIONS) marc_to_txt.c
marc_to_txt.c: e_marc.h
	$(CC) $(OPTIONS) marc_to_txt.c


txt_to_marc: txt_to_marc.o MARC_subs.o
	$(CC) -o txt_to_marc txt_to_marc.o MARC_subs.o 
txt_to_marc.o: txt_to_marc.c
	$(CC) $(OPTIONS) txt_to_marc.c
txt_to_marc.c: e_marc.h
	$(CC) $(OPTIONS) txt_to_marc.c
