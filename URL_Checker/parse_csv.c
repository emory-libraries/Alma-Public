/*
 *  * parse_csv reads a CSV file from standard input.
 ** it assumes that the field delimiter is ";".
 ** it transforms file to text file with _|_ as a delimiter.
 ** it supports UTF-8.
 ** command line option -d delimiter changes the default delimiter.
 ** author: bernardo gomez
 ** date: october, 2017.
 **
 ** 
  */
#include        <stdio.h>
#include        <stdlib.h>
#include	<string.h>
#include	<wchar.h>
#include	<locale.h>
#include	<errno.h>
#include        <unistd.h>

static void givehelp(char *name){
     fprintf(stderr,"   %s\n", "parse_csv - parse a CSV  file.");
     fprintf(stderr,"   %s\n", "usage: cat input_file | parse_csv [-d delimiter]");
     fprintf(stderr,"   %s\n", "default delimiter is \";\"");
     fprintf(stderr,"   %s\n", "output delimiter is _|_");

      }

int main (int argc, char *argv[]){
#define		MAX_LINE_SIZE	21000
#define		MAX_OUT_SIZE	2*21000
#define		INITIAL 	0 
#define		NEW_FIELD       1 
#define		QUOTED_FIELD    2 
#define		REGULAR_FIELD   3 
#define		END_OF_QUOTE    4 
#define		OPTION_LEN      10
#define		QUOTE           L'"' 
#define		YES             1
#define		NO              2 

  extern  void givehelp(char* name);
  extern char *optarg;
  extern int optind, opterr, optopt;

  int		i;
  int		k;
  int           length;
  int           state;
  int           opt;
  int           help;
  wchar_t       external_delim[OPTION_LEN];
  wchar_t       DELIMITER[2];
  wchar_t*	OUT_DELIMITER=L"_|_";
  wchar_t       default_delim[2];
  wchar_t*	savechar;
  wchar_t               line[MAX_LINE_SIZE];
  wchar_t		output[MAX_OUT_SIZE];
  wchar_t		nextchar[2];
  setlocale(LC_ALL, "en_US.UTF-8");
  clearerr(stdin);
  i=0;
  k=0;
  nextchar[1]=L'\0';
  output[0]=L'\0';
  DELIMITER[1]=L'\0';
  state=INITIAL;
  external_delim[0]='\0';
  default_delim[0]=L';';
  help=NO;
  while ((opt = getopt (argc, argv, "hd:")) != -1) {
    switch (opt) {
      case 'h':
        help=YES;
        break;
      case 'd':
         mbstowcs(external_delim,optarg,OPTION_LEN-1);
         external_delim[OPTION_LEN-1]=L'\0';
        break;
      default:
         fprintf(stderr, "Usage: %s [-hs] \n", argv[0]);
    }
    if  (help == YES){
        givehelp(argv[0]);
        exit(0);
    }
  }
  if (wcslen(external_delim) > 0){
       DELIMITER[0]=external_delim[0];
  }
  else{
       DELIMITER[0]=default_delim[0];
  }
  while(fgetws(line,MAX_LINE_SIZE,stdin)!=NULL){
      i=0;
      state=INITIAL;
      output[0]=L'\0';
      line[wcslen(line)-1]='\0';  /* delete LF */
      line[MAX_LINE_SIZE-1]='\0';  /* string safety */
      length=wcslen(line);
      while (i < length){
         if (wcslen(output)+wcslen(OUT_DELIMITER) > MAX_OUT_SIZE){
            fwprintf(stdout,L"%S\n",output);
            break;
         }
         if (state == INITIAL){
            if (line[i] == DELIMITER[0]){
               state=NEW_FIELD;
            }
            else{
               nextchar[0]=line[i];
	       wcscat(output,nextchar);
               state=REGULAR_FIELD;
            }
         }
         else if (state == REGULAR_FIELD){
            if (line[i] == DELIMITER[0]){
               state=NEW_FIELD;
            }
            else{
               nextchar[0]=line[i];
	       wcscat(output,nextchar);
            }
         }
         else if (state == QUOTED_FIELD){
             if (line[i] == QUOTE) {
                state=END_OF_QUOTE;
             }
             else{
               nextchar[0]=line[i];
	       wcscat(output,nextchar);
             }
             
         }
         else if (state == NEW_FIELD){
            if (line[i] == QUOTE){
               wcscat(output,OUT_DELIMITER);
               state=QUOTED_FIELD;
            }
            else if  (line[i] == DELIMITER[0]){
               wcscat(output,OUT_DELIMITER);
            }
            else{
	       wcscat(output,OUT_DELIMITER);
               nextchar[0]=line[i];
	       wcscat(output,nextchar);
               state=REGULAR_FIELD;
            }
         }
         else if (state == END_OF_QUOTE){
            if (line[i] == DELIMITER[0]){
               state=NEW_FIELD;
            }
            else{
               nextchar[0]=line[i];
	       wcscat(output,nextchar);
            }
         }
         else{
		fwprintf(stderr,L"%S\n",L"UNKNOWN STATE");
         }
         i=i+1;
      }
      if (state == NEW_FIELD){
               wcscat(output,OUT_DELIMITER);
      }
      if (wcslen(output) > 0){
           fwprintf(stdout,L"%S\n",output);
      } 
  }       
  if (ferror(stdin)){
	perror("error in stdin");
  }
}

