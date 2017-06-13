#ifndef	_MARC_H
#define	_MARC_H
#define	MARC_rec_status		5
#define	MARC_base_address	12
#define	MARC_directory		24
#define		PRIVATE	static
#define		PUBLIC	
struct _marc{
	unsigned char	*record;
	int 	base_address;
	int	directory_size;
	int	bad;
};
typedef	struct _marc  MARC;
 /* class methods	*/
extern	MARC	*MARC_new(FILE *, char *rec_len);
extern	void 	MARC_delete(MARC *);
extern	int	MARC_displayEntry(MARC *, char *entryID);
extern	int	MARC_displayAll(MARC *);
#endif /* _MARC_H */

