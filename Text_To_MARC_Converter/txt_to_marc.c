#include	<signal.h>
#include	<stdio.h>
#include	<stdlib.h>
#include	<setjmp.h>
#include	<string.h>
#include	<ctype.h>
#include	<time.h>
#include	<fcntl.h>
#include	<errno.h>
#include	<sys/wait.h>
#include	<unistd.h>
#define     PRIVATE static
#define		MAX_NUMBER_FIELDS  4000
#define	    DIRECTOTY_SIZE		24001
#define	    FIELD_SIZE		    10001
#define	    LEADER_LEN		    24
#define	    INPUT_LENGTH    	10500
#define     NEW_RECORD	        "*****"
#define     SUBFIELD_DELIMITER	  '\x1f'
#define     FIELD_TERMINATOR	'\x1e'
#define     RECORD_TERMINATOR	'\x1d'
#define     INIT		0 
#define     READING_REC   1
#define		YES		1
#define		NO 		0

struct _field {
	char id[4];
	char* content;
};
typedef struct _field MARC_FIELD;

PRIVATE void givehelp();
PRIVATE void init_fields(MARC_FIELD [], int);
PRIVATE void produce_marc_string(char*, MARC_FIELD [], int);
PRIVATE char*  replace_string(char* , char* , char* );
PRIVATE void release_storage(MARC_FIELD [], int );

main (int argc, char *argv[]){


  MARC_FIELD field[MAX_NUMBER_FIELDS];
  char  directory[DIRECTOTY_SIZE];
  char  field_work[FIELD_SIZE];
  char  line[INPUT_LENGTH];
  char  leader[25];
  int   first_record=YES;
  int   first_line=YES;
  long  int   field_id;
  char  work_str[5];
  char* end_str;
  int   state=INIT;
  int   next_entry;
  char* ptr;
  
  int  found_record=0;
  int i;
  next_entry=0;
  
  init_fields(field,MAX_NUMBER_FIELDS);

  while (fgets(line,INPUT_LENGTH-1,stdin)!=NULL){
     line[strlen(line)-1]='\0';
     if (state == INIT){
       if (memcmp(line,NEW_RECORD,strlen(NEW_RECORD)) != 0){
  /* not a MARC text file */
         fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"INVALID MARC record");
	     exit(1);
       }
       found_record=1;
       state=READING_REC;
       continue;
     }
     if (state == READING_REC){
       if (memcmp(line,NEW_RECORD,strlen(NEW_RECORD)) == 0){
	      produce_marc_string(leader,field, next_entry);

 /** testing **
    for (i=0;i<next_entry;i++){
      fprintf(stderr,"%s|%s\n",field[i].id,field[i].content);
	}
**/
          release_storage(field, next_entry);
          init_fields(field,MAX_NUMBER_FIELDS);
          next_entry=0;
	      continue;
       }
       memcpy(work_str,line,3);
       work_str[3]='\0';
       errno=0;
       field_id=strtol(work_str, &end_str,10);
       if (errno != 0){
           fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"TAG ID is missing");
	       exit(1);
       }
       if (*end_str != '\0'){
               fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"TAG ID must have three digits");
               fprintf(stderr,"**ERR: %s:\n",line);
	           continue;
       }
       if (field_id==0){
    /* this is the leader */
	       strncpy(leader,line+5,24);
           leader[24]='\0';
	   }
       else if (field_id < 10){
          if (line[4]!= '|'){
               fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"field as an invalid format");
               fprintf(stderr,"**ERR: %s:\n",line);
	           exit(1);
	      }
          /* process field */
          if (next_entry ==  MAX_NUMBER_FIELDS){
               fprintf(stderr,"%s(%d): %s %d\n",__FILE__,__LINE__,"too many MARC fields. maximum: MAX_NUMBER_FIELDS");
               fprintf(stderr,"**ERR: %s:\n",line);
	           exit(1);
	      }
          memcpy(field[next_entry].id,work_str,3);
          field[next_entry].id[3]='\0';

/* allocate 100 extra bytes for safety.  */
          if ((field[next_entry].content=calloc(1,strlen(line+5)+100))==NULL){
               fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"calloc failed");
               fprintf(stderr,"**ERR: %s:\n",line);
	           exit(1);
          }
          strcpy(field[next_entry].content,line+5);

		  next_entry++;
	   }
       else{
          if (line[6]!= '|'){
               fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"field has an invalid format");
               fprintf(stderr,"**ERR: %s:\n",line);
	           exit(1);
		  }
          if (next_entry ==  MAX_NUMBER_FIELDS){
               fprintf(stderr,"%s(%d): %s %d\n",__FILE__,__LINE__,"too many MARC fields. maximum: MAX_NUMBER_FIELDS");
               fprintf(stderr,"**ERR: %s:\n",line);
	           exit(1);
	      }
          /* process field */
          memcpy(field[next_entry].id,work_str,3);
          field[next_entry].id[3]='\0';
/* allocate 100 extra bytes for safety.  */
          if ((field[next_entry].content=calloc(1,strlen(line+5)+100))==NULL){
               fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"calloc failed");
               fprintf(stderr,"**ERR: %s:\n",line);
	           exit(1);
          }
          memcpy(field[next_entry].content,line+4,1);
          memcpy(field[next_entry].content+1,line+5,1);
          strcpy(field[next_entry].content+2,line+7);
		  next_entry++;
	   }
     }
  }
  if (found_record == 1){
     produce_marc_string(leader,field, next_entry);
  }
  release_storage(field, next_entry);
  init_fields(field,MAX_NUMBER_FIELDS);
 /** testing **/
    for (i=0;i<next_entry;i++){
     /*  fprintf(stdout,"%s|%s\n",field[i].id,field[i].content); */
	}
  exit(0);
}

void init_fields(MARC_FIELD field[], int max_field){
  int i;
  for (i=0;i<max_field;i++){
       field[i].content=NULL;
  }
  return;
}

void release_storage(MARC_FIELD field[], int max_field){
  int i;
  for (i=0;i<max_field;i++){
       if (field[i].content != NULL){
	      free(field[i].content);
       }
       field[i].content=NULL;
  }
  return;
}

void produce_marc_string(char* leader, MARC_FIELD field[], int field_count){
  char* ptr;
  unsigned  char subfield_delim[2];
  int 		i;
  int		k;
  int		dir_length;
  int		text_length;
  int		record_length;
  char* 	directory;
  char* 	text;
  char* 	record;
  int		previous_offset;
  int		previous_length;
  char* 	here;
  int 		first_field=YES;
  char		number_str[6];
  
  subfield_delim[0]=SUBFIELD_DELIMITER;
  subfield_delim[1]='\0';
  for (i=0;i<field_count;i++){
    while ((ptr=replace_string(field[i].content,"\\p",subfield_delim))!=NULL);
  }
  for (i=0;i<field_count;i++){
     k=strlen(field[i].content);
     field[i].content[k]=FIELD_TERMINATOR;
     field[i].content[k+1]='\0';
  }
  dir_length=0;
  text_length=0;

  for (i=0;i<field_count;i++){
    text_length+=strlen(field[i].content);
  }

  dir_length=field_count*12;
  dir_length+=2;  /* directory ends with a SUBFIELD_DELIMITER */
  text_length+=2; /* records ends with a RECORD_TERMINATOR */

  sprintf(number_str,"%5.5d",(field_count*12)+1+24);
  memcpy(leader+12,number_str,5);

  if ((directory=(char *)calloc(1,dir_length))==NULL){
     fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"calloc failed");
     return;
  }
  if ((text=(char *)calloc(1,text_length))==NULL){
     fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"calloc failed");
     return;
  }
  previous_offset=0;
  previous_length=0;

  here=directory;
  for (i=0;i<field_count;i++){
    if (first_field==YES){
      memcpy(here,field[i].id,3);
      sprintf(here+3,"%4.4d", strlen(field[i].content));
      sprintf(here+7,"%5.5d", 0);
      previous_length=0;
	  previous_offset=strlen(field[i].content);
      here+=12;
      first_field=NO;
    }
    else{
      memcpy(here,field[i].id,3);
      sprintf(here+3,"%4.4d", strlen(field[i].content));
      sprintf(here+7,"%5.5d",previous_offset+previous_length);
      previous_offset=previous_offset+previous_length;
      previous_length=strlen(field[i].content);
      here+=12;
    }
  }
  directory[dir_length-2]=FIELD_TERMINATOR;
  directory[dir_length-1]='\0';

/**
  fprintf(stderr,"leader: %s\n",leader);
  fprintf(stderr,"directory: %s\n",directory);
**/
  
  text[0]='\0';
  for (i=0;i<field_count;i++){
    strcat(text,field[i].content);
  }
  text[text_length-2]=RECORD_TERMINATOR;
  text[text_length-1]='\0';

  record_length=24+strlen(directory)+strlen(text)+1;
  if ((record=(char *)calloc(1,record_length))==NULL){
     fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"calloc failed");
     return;
  }
  record[0]='\0';
  strcat(record,leader);
  strcat(record,directory);
  strcat(record,text);
  sprintf(number_str,"%5.5d",record_length-1);
  memcpy(record,number_str,5);
  fprintf(stdout,"%s",record);
  free(record);
  free(text);
  free(directory);
  return;
}

char* replace_string(char* source, char* str_from, char* str_to){
  char* work;
  char* ptr;

  if ((work=(char *)calloc(1,strlen(source)+strlen(str_to)+1))==NULL){
     fprintf(stderr,"%s(%d): %s\n",__FILE__,__LINE__,"calloc failed");
     return NULL;
  }
  *work='\0';
  
  if ((ptr=strstr(source,str_from))==NULL){
      free(work);
      return(NULL);
  }
  *ptr='\0';
  strcat(work,source);
  strcat(work,str_to);
  strcat(work,source+strlen(source)+strlen(str_from));
  strcpy(source,work);
  free(work);
  return(source);
}

void givehelp(){
}
