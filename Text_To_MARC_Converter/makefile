CC = /usr/bin/gcc 
OPTIONS = -c -g

all: txt_to_marc

txt_to_marc: txt_to_marc.o
  $(CC) -o txt_to_marc txt_to_marc.o
txt_to_marc.o: txt_to_marc.c
  $(CC) $(OPTIONS) txt_to_marc.c
