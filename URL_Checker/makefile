CC = /usr/bin/gcc 
OPTIONS = -c -g
# usage: make -f makefile parse_csv
# cp parse_csv to-bin-directory

all: parse_csv
parse_csv.o: parse_csv.c
  $(CC) $(OPTIONS) parse_csv.c
parse_csv: parse_csv.o
  $(CC) -o parse_csv parse_csv.o 
