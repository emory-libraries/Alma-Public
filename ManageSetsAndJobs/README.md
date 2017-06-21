# Manage Sets and Jobs

#### Python 2.7.5

#### bash 4.2.46(1)

#### Contributors: Alex Cooper, Bernardo Gomez, Elizabeth Peele Mumpower

#### Dependencies: needs job xml

#### Purpose: automate set creation, management, and deletion and job usage

------------------------------------

## Under Construction!

------------------------------------

### [shell scripts](https://github.com/Emory-LCS/Alma-Public/tree/master/ManageSetsAndJobs/shell) to run all of the [python scripts](https://github.com/Emory-LCS/Alma-Public/tree/master/ManageSetsAndJobs/python)

#### cronjobs:

> 11 17 * * * bash /sirsi/webserver/bin/set_management_alma.sh 2> /tmp/set_management_$$.err

> 23 23 * * * bash /sirsi/webserver/bin/delete_alma_set.sh 2> /tmp/set_delete_$$.err

> 30 7 1 * * bash /sirsi/webserver/bin/run_browzine_job.sh 2> /tmp/browzine_sh_err_$$.txt

-----------
