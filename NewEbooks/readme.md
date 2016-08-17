python version 2.7.5
bash version 4.1.2(1)
Purpose: Flag items acquired in the last 60 days to create a Newly Acquired flag for Primo
Dependencies: the api scripts are using the socks and socket modules to place api calls via bela
-------------------------------------------------------------------------------------------------
master script to run the newly acquired scripts below
added to crontab
26 11 * * * bash /alma/bin/newly_acquired.sh 2> /tmp/newly_acquired.log
-------------------------------------------------------------------------------------------------
