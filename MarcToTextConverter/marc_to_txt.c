/**
 ** Author: Bernardo Gomez
 ** Date:   March, 2000.
 ** Description: Program reads a MARC record in the standard input, and
	writes fields on plain ASCII to standard output.
 ** 	Tags are pipe-delimited. Subfield delimiters are spelled out as "\p"
 ** 	Default option is to show all fields. A list of tags can be indicated
 **	by -e tag1,tag2,...
 **	Ill-formed MARC records are written to standard error.
**/
#include	<signal.h>
#include	<stdio.h>
#include	<stdlib.h>
#include	<setjmp.h>
#include	<string.h>
#include	<ctype.h>
#include	<time.h>
#include	<fcntl.h>
#include	<sys/wait.h>
#include	<unistd.h>
#include        "e_marc.h"
/*  #include	"utils.h" */

PRIVATE char *u_timestamp(){
#define MAX_TSTR        60
 time_t ctime;
 struct tm      *today;
 static char    t_str[MAX_TSTR+1];
    time(&ctime);
    today=localtime(&ctime);
    strftime(t_str, MAX_TSTR,"%A, %B %d, %Y, %H:%M %p", today);
    return(t_str);
}



PRIVATE	 char	**getFields(char *line, char separator){
 static	char	**field;
 char		**temp;
 char		*ptr;
 char		*delim;
 char		saveit;
 int		count;
	count=0;
	ptr=line;
	while (*ptr != '\0'){
		count++;
		if ((delim=strchr(ptr,separator))==NULL){
			break;
		}
		ptr=delim+1;
	}
	count++;
	ptr=line;
	if ((field=(char **)calloc(1,count*sizeof(char *))) == NULL){
		fprintf(stderr,"%s\n","Memory allocation failed. utils.c");
		return	NULL;
	}
	temp=field;
	while (*ptr != '\0'){
		if ((delim=strchr(ptr,separator))==NULL){
			if ((*temp=(char *)calloc(1,strlen(ptr)+1))==NULL){
				fprintf(stderr,"%s(%d) memory alloc. failed",
				__FILE__,__LINE__);
				return NULL;
			}
			strcpy(*temp,ptr);
			temp++;
			break;
		}
		saveit=*delim;
		*delim='\0';
		if ((*temp=(char *)calloc(1,strlen(ptr)+1))==NULL){
			fprintf(stderr,"%s(%d) memory allocation failed",
			__FILE__,__LINE__);
			return NULL;
		}
		strcpy(*temp,ptr);
		*delim=saveit;
		temp++;
		ptr=delim+1;
	}
	*temp=NULL;
	return field;
}


PRIVATE void givehelp();
main (int argc, char *argv[]){
 extern		char	**getFields(char *, char );
 extern char    **environ;
 extern int 	optind;
 extern int 	optopt;
 extern int 	opterr;
 extern char 	*optarg;
 char		*e_list;
 char		*ptr;
 int		done;
 int		c;
 int		all_entries;
 char    	**entry;
 char    	**tmp;
 char		rec_len[6];
 int		i;
 int		it_is_a_digit;
 int		recLen;
 MARC		*marc;
 static		char	ALLTAGS[]="ALL";
 /** validate requests and status **/
  all_entries=0;
  done=0;
  e_list=NULL;
  while ((c = getopt(argc, argv, "e:h")) != -1) {
        switch(c) {
                case '?':
			fprintf(stderr,"%s\n","INVALID OPTION");
                        done=1;
                break;
                case 'e':
                      e_list=optarg;
                break;
                case 'h':
			done=1;
                break;
        }
  }
  if (done ==1){
	givehelp();
	return 1;
  }
  if (e_list==NULL)
	e_list=ALLTAGS;
  for (ptr=e_list; *ptr; ptr++)
	*ptr=toupper(*ptr);
  if (strcmp(e_list,"ALL")==0){
	all_entries=1;
  }
  else if ((entry=getFields(e_list,','))==NULL){
	fprintf(stderr,"%s\n","Entry list in error");
	givehelp();
	return 1;
  }
  while  (fread(rec_len,5,1,stdin)==1){
	memset(rec_len+5,'\0',1);
	ptr=rec_len;
	it_is_a_digit=1;
	while(*ptr){
		if (!isdigit((int) *ptr)){
			it_is_a_digit=0;
		}
		ptr++;
	}
	if (! it_is_a_digit){
		fprintf(stderr,"%s\n","this file is not a MARC file. leader (0-4) is not a record length");
		exit(1);
	}
	recLen=strtol(rec_len,NULL,10);
	marc=MARC_new(stdin, rec_len);
	if (marc == NULL){
		fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"MARC_new failed");
		return 1;
	}
	if (marc->bad){
		fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"INVALID MARC record");
		*(marc->record+recLen-1)='\0';
		fprintf(stderr,"%s\n",marc->record);
		/* return 1; */
                continue;
  	}
	fprintf(stdout,"%s\n","*******");
	if (all_entries){
		MARC_displayAll(marc);
	}
	else{
		tmp=entry;
		while (*tmp != NULL){
			MARC_displayEntry(marc, *tmp);
			tmp++;
		}
	}
	MARC_delete(marc);
  }
  return 0;
}
/*** ***/
PRIVATE void opening(){
 char *u_timestamp();
 fprintf(stderr,"requests started on  %s\n",u_timestamp());
}
/*** ***/
PRIVATE void closing(int selected){
 char *u_timestamp();
 fprintf(stderr,"   %d record(s) processed\n", selected);
 fprintf(stderr,"requests finished on %s\n",u_timestamp());
}
/*** ***/
PRIVATE void givehelp(){
   fprintf(stderr,"%s\n","   marc_to_txt reads a MARC record in the standard input and produces");
   fprintf(stderr,"%s\n","   a list of MARC fields");
   fprintf(stderr,"%s","     as plain text on the standard output.");
  fprintf(stderr,"%s\n"," Each MARC field occupies a line");
   fprintf(stderr,"%s\n","   A line has the format: TAG|INDIC|text|");
  fprintf(stderr,"%s\n","    TAG is the Tag ID.");
  fprintf(stderr,"%s\n","    INDIC is the two indicator digits.");
  fprintf(stderr,"%s\n","    Text is the field text. A subfield separator is represented by \\p");
  fprintf(stderr,"%s\n","    The leader is represented by field 000");
  fprintf(stderr,"%s\n","    Fields 000-009 do not have indicators.");
  fprintf(stderr,"%s\n","    Each record starts with the line *****");
  fprintf(stderr,"%s\n","    Options:");
  fprintf(stderr,"%s\n","      -e xxx,xxx,...  to display selected tags");
  fprintf(stderr,"%s\n","      -e ALL          to display all      tags");
}
/*** ***/
PRIVATE	char *e_trandate(){
#define MAX_TSTR        60
 time_t ctime;
 struct tm      *today;
 static char    t_str[MAX_TSTR+1];
    time(&ctime);
    today=localtime(&ctime);
    strftime(t_str, MAX_TSTR,"%Y%m%d%H%M", today);
    return(t_str);
}
