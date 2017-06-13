#include        <sys/types.h>
#include        <errno.h>
#include        <string.h>
#include        <ctype.h>
#include        <stdio.h>
#include        <stdlib.h>
#include        <unistd.h>
#define         SERVER_DOWN "API server is down. Please, try later."
#define         FATAL_ERROR "Fatal error. Transaction failed."
#include        "e_marc.h"
/***
main(int argc, char *argv[]){
 MARC	*me;
 me=MARC_new("/s/sirsi/Unicorn/Bincustom/Develop/junk.serv");
 MARC_delete(me);
 fprintf(stderr,"%s\n",MARC_next(me));
 fprintf(stderr,"%s\n",MARC_next(me));
 fprintf(stderr,"%s\n",MARC_next(me));
 fprintf(stderr,"***\n%s\n",MARC_get(me,"LANE"));
 MARC_delete(me);
 return 0;
}
***/
PUBLIC	MARC	*MARC_new(FILE *input, char *rec_len){
 MARC	*me;
 char	base_address[6];
 int	recLen;
 int	i;
	recLen=strtol(rec_len, NULL,10);
	if (recLen > 99999){
		fprintf(stderr,"%s(%d): not a valid MARC record.\n",__FILE__,__LINE__);
		return NULL;
	}
        if ((me=(MARC *)calloc(1,sizeof(MARC))) == NULL){
                return NULL;
        }
	if ((me->record=(unsigned char *)calloc(1,recLen))==NULL){
		fprintf(stderr,"%s(%d): Memory allocation\n",__FILE__,__LINE__);
		return NULL;
	}
	me->bad=0;
	memcpy(me->record,rec_len,5);
	if (fread(me->record+MARC_rec_status,recLen-5,1,input)!=1){
		fprintf(stderr,"%s(%d): Invalid MARC record.\n",__FILE__,__LINE__);
		me->bad=1;
		return me;
	}
 /* verify record terminator	*/
	if (*(me->record+recLen-1) != '\x1d'){
		fprintf(stderr,"%s(%d): Invalid MARC record. couldn't find end-of-record.\n",__FILE__,__LINE__);
		me->bad=1;
		return me;
	}
	memcpy(base_address,me->record+MARC_base_address,5);
	memset(base_address+5,'\0',1);
	me->base_address=strtol(base_address,NULL,10);
	me->directory_size=(me->base_address-24)/12;
	return me;
}
/***	***/
PUBLIC	void	MARC_delete(MARC *me){
 int	i;
	if (me == NULL) return;
	free(me->record);
	free(me);
	return;
}
/***	***/
PUBLIC	int     MARC_displayEntry(MARC *me, char *entryID){
 char	*tmp;
 char	*next;
 int	i;
 int	field_len;
 int	ID;
 int	j;
 int	int_c;
 int	start_field;
 int	start_position;
 int	start_char_pos;
 char	number[6];
 char	indicator[3];
 char	fixed_field[30];
 char   *here;
	if (me == NULL) return 1;
	tmp=me->record+MARC_directory;
	here=me->record;
	for (i=0;i<24;i++){
		if ((*here < '\x20')&&(*here != '\x1b')){
			*here=' ';
		}
		here++;
	}
    memcpy(fixed_field,me->record,24);
    fixed_field[24]='\0';
	ID=strtol(entryID,NULL,10);
	if (ID == 0){
	   fprintf(stdout,"000||%s\n",fixed_field);
	   return 0;
	}
	tmp=me->record+MARC_directory;
	for (i=0;i<me->directory_size;i++){
		if (memcmp(tmp,entryID,3)==0){
			memcpy(number,tmp+3,4);
			memset(number+4,'\0',1);
			field_len=strtol(number,NULL,10);
			memcpy(number,tmp+7,5);
			memset(number+5,'\0',1);
			start_position=strtol(number,NULL,10);
			start_char_pos=start_position+me->base_address;
			fprintf(stdout,"%s|",entryID);
			ID=strtol(entryID,NULL,10);
			if (ID < 10){
				fprintf(stdout,"%s|","");

			  	for (j=0;j<field_len-1;j++){
					fprintf(stdout,"%c",*(me->record+
						start_char_pos+j));
				}
			}
			else{
				next=me->record+start_char_pos;
				if (*next == '\x1f'){
					memcpy(indicator,"  ",2);
					start_field=0;
				}
				else{
					memcpy(indicator,next,2);
					start_field=2;
				}
				memset(indicator+2,'\0',1);
				fprintf(stdout,"%s|",indicator);
				for (j=start_field;j<field_len-1;j++){
					if (*(next+j) =='\x1f'){
						if (*(next+j+1) =='\x1f'){
							continue;
						}
  /*** try to fix sirsi's flaw: replace an invalid 
	subfield delimiter with a "|"
 ***/
						int_c=(int)*(next+j+1);
						if (islower(int_c)||isdigit(int_c)|| *(next+j+1)=='='||*(next+j+1)=='?'){
						  fprintf(stdout,"%s","\\p");
						}
						else{
						  fprintf(stdout,"%s","|");
						}
					}
					else{
						if (*(next+j) =='\x0a'){
							*(next+j)=' ';
						}
						fprintf(stdout,"%c",*(next+j));
					}
				}
			}
			fprintf(stdout,"%s","\n");
		}
		tmp+=12;
	}
	return 0;
}
PUBLIC	int	MARC_displayAll(MARC *me){
 char	*tmp;
 char 	*here;
 char	*next;
 int	i;
 int	int_c;
 int	field_len;
 int	start_position;
 int	start_char_pos;
 int	ID;
 int	j;
 char	number[6];
 char	indicator[3];
 char	entryID[4];
 char	fixed_field[12];
	if (me == NULL) return 1;
	tmp=me->record+MARC_directory;
	here=me->record;
	for (i=0;i<24;i++){
		if ((*here < '\x20')&&(*here != '\x1b')){
			*here=' ';
		}
		here++;
	}

    memcpy(fixed_field,me->record,24);
    fixed_field[24]='\0';
	fprintf(stdout,"000||%s\n",fixed_field);

	for (i=0;i<me->directory_size;i++){
		memcpy(entryID,tmp,3);
		memset(entryID+3,'\0',1);
		memcpy(number,tmp+3,4);
		memset(number+4,'\0',1);
		field_len=strtol(number,NULL,10);
		memcpy(number,tmp+7,5);
		memset(number+5,'\0',1);
		start_position=strtol(number,NULL,10);
		start_char_pos=start_position+me->base_address;
		fprintf(stdout,"%s|",entryID);
		ID=strtol(entryID,NULL,10);
		if (ID < 10){
		  fprintf(stdout,"%s","|");

		  for (j=0;j<field_len-1;j++){
			fprintf(stdout,"%c",*(me->record+ start_char_pos+j));
		  }
		}
		else{
		  memcpy(indicator,me->record+start_char_pos,2);
		  memset(indicator+2,'\0',1);
		  fprintf(stdout,"%s|",indicator);
		  for (j=2;j<field_len-1;j++){
			next=me->record+start_char_pos;
			if (*(next+j) =='\x1f'){
				if (*(next+j+1)=='\x1f'){
					continue;
				}
  /*** try to fix sirsi's flaw: replace an invalid 
	subfield delimiter with a "|"
 ***/
				int_c=(int)*(next+j+1);
				if (islower(int_c)||isdigit(int_c)||
					*(next+j+1)=='='||
					*(next+j+1)=='?'){
					fprintf(stdout,"%s","\\p");
				}
				else{
					fprintf(stdout,"%s","|");
				}
			}
			else{
				if (*(next+j) =='\x0a'){
					*(next+j)=' ';
				}
				fprintf(stdout,"%c",*(next+j));
			}
		  }
		}
		fprintf(stdout,"%s","\n");
		tmp+=12;
	}
}
/***	***/

