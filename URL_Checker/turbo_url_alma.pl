#!/usr/bin/perl -w 
### Purpose: This is the URL checker's driver. It reads UNICORN produced 
###		file; it parses the file to produce a text file with
###		pipe-delimited lines.
###		A pipe-delimited line would contain:
###		"URL|title_control_key|holding libraries|"
###		holding libraries are represented by the policy numbers.
###	     The pipe-delimited file is fed to the urlcheker program.
###  Author: Bernardo Gomez.  March, 2006.
###  Customization:   1) change perl path.
###		      2) this script can run in any UNIX system,
###		including LINUX. script doesn't have any UNICORN
###		dependencies. 
###		     3) change sendmail's path to reflect your local
###			server.
###		     4) add extra perl code if the UNICORN file
###			contains other MARC tags with URLs. See parse_input
###		      subroutine for clues.
### 			This script only parses 856 tags as delivered.
use strict;
use integer;
use Getopt::Std;
sub relocated;
sub bad_request;
sub internal_error;
sub defective_response;
sub pass_required;
sub forbidden;
sub not_found;
sub print_log;
sub unknown_host;
sub refused_by_server;
sub unsupported;
sub bad_url;
sub cleanup;
sub exclude_them;
sub parse_input;
sub opening;
sub closing;
sub give_help;
our ($opt_d,$opt_e,$opt_f,$opt_i,$opt_m,$opt_n,$opt_t,$opt_x);
my $exception;
my $input;
my $selected=0;
my $considered=0;
my $line;
my $i;
my $mail_list;
my $url_list;
my $number_threads;
my $chunk_size;
my $status;
my $chunk_file_name;
my $output;
my $tempdir;
my %mail_info;
my $chunk_name;
my $total_lines=0;
my $remainder;
my $libr_number;
my $libr_name;
my $mail_address="bgomez\@emory.edu";
my $reply_to="alma\@turing.library.emory.edu";
my $time_out=10;  ## 20 seconds is a good value.
my $email_body="";
my $email_message="";
my $Subject="";
$number_threads=4;
$exception="";
$input="";
getopts('xe:n:i:m:t:d:');
opening();
$tempdir="/tmp/";
$tempdir="/alma/integrations/urlCheck/work/";
# unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
#   print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
#   exit 1;
#}
$mail_list="sirsi\@mail.library.emory.edu";
if (defined($opt_e)){
	$exception=$opt_e;
}
if (defined($opt_i)){
	$input=$opt_i;
}
if (defined($opt_m)){
	$mail_list=$opt_m;
}
if (defined($opt_n)){
	$number_threads=$opt_n;
}
if (defined($opt_d)){
	$time_out=$opt_d;
}
if (defined($opt_t)){
	$tempdir=$opt_t;
}
if (defined($opt_x) || $input eq ""){
 give_help();
 closing($considered,$selected,$total_lines);
 exit 0;
}
$output="$tempdir/out_parser_"; 
$url_list="$tempdir/urls_";
if ($input eq ""){
	print STDERR "**ERR $0: input file is missing\n";
	print STDERR "** $0: run select_urls.pl to obtain $input file\n";
	print_log();
 	closing($considered,$selected,$total_lines);
	exit 1;
}

#
if ($mail_list ne ""){ 
	unless(open(MAIL_LIST,"<",$mail_list)){
		print STDERR "**ERR $0: couldn't open mail list $mail_list\n";
		exit 1;
	}
	while($line=<MAIL_LIST>){
		chomp($line);
		($libr_number,$libr_name,$mail_address)=split(/\|/,$line);
		$mail_address=~s/,/ /;
		$mail_info{$libr_number}="$libr_name|$mail_address|";
	}
	close(MAIL_LIST);
}

# count is the desired number of background processes .
####$status=parse_input($input,$url_list);
$url_list=$input;
$status=0;
if ($status != 0){
	print STDERR "**ERR $0: couldn't parse input file\n";
	exit 1;
}
if ($exception ne ""){
	$status=0;
 	if (!-s $exception){
		print STDERR "**WARNING: $0 exception file $exception doesn't exist\n";
		$output=$url_list;
	}
	else{
		$status=exclude_them($url_list,$output,$exception);
	}
}
else{
	$output=$url_list;
}
if ($status != 0){
	print STDERR "**ERR $0: couldn't process exception list\n";
	print_log();
 	closing($considered,$selected,$total_lines);
	exit 1;
}
unless(open(URL_FILE,"<",$output)){
	print STDERR "**ERR $0: couldn't open url file $output\n";
	print_log();
 	closing($considered,$selected,$total_lines);
	exit 1;
}
$total_lines=0;
my @unsorted;
@unsorted=<URL_FILE>;
close(URL_FILE);
my @sorted_list;
@sorted_list=sort @unsorted;
$total_lines=scalar(@sorted_list);
$chunk_size=$total_lines/$number_threads;
$remainder=$total_lines%$number_threads;
if ($remainder > 0){
 $number_threads+=1;
}
### split file into $number_threads.
$chunk_name="aaa";
unless(open(URL_FILE,"<",$output)){
	print STDERR "**ERR $0: couldn't open url file $url_list\n";
	print_log();
 	closing($considered,$selected,$total_lines);
	exit 1;
}
$i=0;
$chunk_file_name="$tempdir/chunk_$chunk_name";
unless(open(CHUNK,">","$chunk_file_name")){
	print STDERR "**ERR $0: couldn't open chunk file $chunk_file_name\n";
	print_log();
 	closing($considered,$selected,$total_lines);
	exit 1;
}
LOOP: foreach $line (@sorted_list){
 if ($i == $chunk_size){
	close(CHUNK);
	$chunk_name++;
	if ($chunk_name eq "zzz"){
		print STDERR "WARNING $0: you're trying to split url file in too many chunks!\n";
		next LOOP;
	}
	$chunk_file_name="$tempdir/chunk_$chunk_name";
	unless(open(CHUNK,">","$chunk_file_name")){
		print STDERR "**ERR $0: couldn't open chunk file $chunk_file_name\n";
		print_log();
 		closing($considered,$selected,$total_lines);
		exit 1;
	}
	$i=0;
	$status=print CHUNK "$line";
	if ($status == 0){
		print STDERR "**ERR $0: couldn't write onto $chunk_file_name\n";
		print_log();
 		closing($considered,$selected,$total_lines);
		exit 1;
	}
	$i++;
 }
 else{
	$status=print CHUNK "$line";
	if ($status ==0){
		print STDERR "**ERR $0: couldn't write onto $chunk_file_name\n";
		print_log();
 		closing($considered,$selected,$total_lines);
		exit 1;
	}
 	$i++;
 }
}
close(CHUNK);
close(URL_FILE);
### create $number_threads background processes
$chunk_name="aaa";
my @processID;
my $result_file;
my $input_urls;
my $fork_failed=0;
unlink("$tempdir/checkurl.log");
for ($i=0;$i<$number_threads;$i++){
	if (!defined($processID[$i] = fork())) {
		$fork_failed+=1;
	}
	elsif ($processID[$i] ==0){
		## this is the child. you may do work.
		$result_file="$tempdir/url_result_$chunk_name";
		$input_urls="$tempdir/chunk_$chunk_name";
		#qx%checkurl.pl -t $time_out < $input_urls 2>> $tempdir/checkurl.log > $result_file%;
		qx%curl_to_checkurl.sh -t $time_out < $input_urls 2>> $tempdir/checkurl.log > $result_file%;
		sleep 2;
		exit 0;
	}
	$chunk_name++;
}
if ($fork_failed ==0){
	for ($i=0; $i< $number_threads; $i++){
		waitpid($processID[$i], 0);
	}
}
else{
	print STDERR "**ERROR $0: fork failed\n";
	print STDERR "**ERROR $0: only one thread will be executed\n";
	qx%checkurl.pl  < $input_urls 2>> $tempdir/checkurl.log > $result_file%;
}
my $union_file;
$chunk_name="aaa";
for ($i=0;$i<$number_threads;$i++){
   unlink("$tempdir/chunk_$chunk_name");
   $chunk_name++;
}
$union_file="$tempdir/all_processed_urls";
print STDERR "**INFO $0: about to write processed URLs\n";
unless(open(UNION,">",$union_file)){
		print STDERR "**ERR $0: couldn't write onto $chunk_file_name\n";
		print_log();
 		closing($considered,$selected,$total_lines);
		exit 1;
}
$chunk_name="aaa";
$result_file="$tempdir/url_result_$chunk_name";
for ($i=0;$i<$number_threads;$i++){
	unless(open(CHUNK,"<",$result_file)){
		print STDERR "**ERR $0: couldn't open $result_file\n";
		print_log();
 		closing($considered,$selected,$total_lines);
		exit 1;
	}
	while($line=<CHUNK>){
		$status=print UNION "$line";
		if ($status ==0){
			print STDERR "**ERR $0: couldn't write onto union_file$\n";
			print_log();
 			closing($considered,$selected,$total_lines);
			exit 1;
		}
	}
	close(CHUNK);
	$chunk_name++;
	$result_file="$tempdir/url_result_$chunk_name";
}
close(CHUNK);
close(UNION);
$union_file="$tempdir/all_processed_urls";
print STDERR "**INFO $0: about to read processed URLs\n";
unless(open(UNION,"<",$union_file)){
		print STDERR "**ERR $0: couldn't open $union_file\n";
		print_log();
 		closing($considered,$selected,$total_lines);
		exit 1;
}
$chunk_name="aaa";
for ($i=0;$i<$number_threads;$i++){
   unlink("$tempdir/url_result_$chunk_name");
   $chunk_name++;
}
my $inet_protocol;
my $return_code;
my $verbose_code;
my $new_target;
my $target;
my $title_key;
my $owning_libraries;
my @bad_request_txt;
my @pass_required_txt;
my @forbidden_txt;
my @not_found_txt;
my @internal_error_txt;
my @unsupported_txt;
my @refused_by_server_txt;
my @unknown_host_txt;
my @defective_response_txt;
my @bad_url_txt;
my $j;
my $libr_entry;
foreach $libr_entry (keys %mail_info){
  #### define response files for each defined library.
	$bad_request_txt[$libr_entry]="";
	$pass_required_txt[$libr_entry]="";
	$forbidden_txt[$libr_entry]="";
	$not_found_txt[$libr_entry]="";
	$internal_error_txt[$libr_entry]="";
	$unsupported_txt[$libr_entry]="";
	$refused_by_server_txt[$libr_entry]="";
	$unknown_host_txt[$libr_entry]="";
	$defective_response_txt[$libr_entry]="";
	$bad_url_txt[$libr_entry]="";
}
HERE1: while($line=<UNION>){
	chomp($line);
	($inet_protocol,$return_code,$verbose_code,$new_target,$target,$title_key,$owning_libraries)=split(/\|/,$line);
	if ($return_code == 200||
		$return_code == 301||
		$return_code == 302||
		$return_code == 303||
		$return_code == 304||
		$return_code == 305||
		$return_code == 307||
		$return_code == 605){
		next HERE1;
	}
	if ($return_code == 400){
		report_URL($title_key,$owning_libraries,$target,\@bad_request_txt);
	}
	elsif ($return_code == 401){
		report_URL($title_key,$owning_libraries,$target,\@pass_required_txt);
	}
	elsif ($return_code == 403){
		report_URL($title_key,$owning_libraries,$target,\@forbidden_txt);
	}
	elsif ($return_code == 404 || $return_code == 410){
		report_URL($title_key,$owning_libraries,$target,\@not_found_txt);
	}
	elsif ($return_code == 500){
		report_URL($title_key,$owning_libraries,$target,\@internal_error_txt);
	}
	elsif ($return_code == 501){
		report_URL($title_key,$owning_libraries,$target,\@unsupported_txt);
	}
	elsif ($return_code == 602){
		report_URL($title_key,$owning_libraries,$target,\@refused_by_server_txt);
	}
	elsif ($return_code == 603){
		report_URL($title_key,$owning_libraries,$target,\@unknown_host_txt);
	}
	elsif ($return_code == 604){
		report_URL($title_key,$owning_libraries,$target,\@defective_response_txt);
	}
	elsif ($return_code == 606){
            #print STDERR "606 code\n";
		report_URL($title_key,$owning_libraries,$target,\@bad_url_txt);
	}
}
## send email messages next.
#my $email_body;
#my $email_message="";
foreach $j (keys %mail_info){
	($libr_name,$mail_address)=split(/\|/,$mail_info{$j});
	if ($bad_request_txt[$j] ne ""){
#/usr/sbin/sendmail -t -bm
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="Server considered this as a BAD REQUEST:\n\n";
                $Subject="urlchecker: bad request [$libr_name]";
                $email_message="To: $mail_address\nFrom: $reply_to\nSubject: $Subject\n\n$email_body";
                
                print MAIL "$email_message";
		close(MAIL);
	}
	if ($pass_required_txt[$j] ne ""){
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="The following objects require authorization:\n\n";
		$email_body.="$pass_required_txt[$j]";
                $Subject="urlchecker: password required [$libr_name]";
                print MAIL "To: $mail_address\nFrom: $reply_to\nSubject: $Subject\n\n$email_body";
		close(MAIL);
	}
	if ($forbidden_txt[$j] ne ""){
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="Access to this object is forbidden:\n\n";
		$email_body.="$forbidden_txt[$j]";
                $Subject=" urlchecker: access forbidden [$libr_name]";
                print MAIL "To: $mail_address\nFrom: $reply_to\nSubject: $Subject\n\n$email_body";
		close(MAIL);
	}
	if ($not_found_txt[$j] ne ""){
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="The following objects were NOT FOUND:\n\n";
		$email_body.="$not_found_txt[$j]";
                $Subject="urlchecker: not found [$libr_name]";
                print MAIL "To: $mail_address\nFrom: $reply_to\nSubject: $Subject\n\n$email_body";
		close(MAIL);
	}
	if ($internal_error_txt[$j] ne ""){
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="Server incapable of fulfilling request:\n\n";
		$email_body.="$internal_error_txt[$j]";
                $Subject="urlchecker: server error [$libr_name]";
                print MAIL "To: $mail_address\nFrom: $reply_to\n$Subject: $Subject\n\n$email_body";
		close(MAIL);
	}
	if ($unsupported_txt[$j] ne ""){
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="Server couldn't parse request:\n\n";
		$email_body.="$unsupported_txt[$j]";
                $Subject="urlchecker: confusing request [$libr_name]";
                print MAIL "To: $mail_address\nFrom: $reply_to\nSubject: $Subject\n\n$email_body";
		close(MAIL);
	}
	if ($refused_by_server_txt[$j] ne ""){
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="Connection was refused by server:\n\n";
		$email_body.="$refused_by_server_txt[$j]";
                $Subject="urlchecker: connection refused [$libr_name]";
                print MAIL "To: $mail_address\nFrom: $reply_to\nSubject: $Subject\n\n$email_body";
		close(MAIL);
	}
	if ($unknown_host_txt[$j] ne ""){
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="Host name doesn't exist:\n\n";
		$email_body.="$unknown_host_txt[$j]";
                $Subject="urlchecker: unknown host [$libr_name]";
                print MAIL "To: $mail_address\nFrom: $reply_to\nSubject: $Subject\n\n$email_body";
		close(MAIL);
	}
	if ($defective_response_txt[$j] ne ""){
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="Couldn't understand server's response:\n\n";
		$email_body.="$defective_response_txt[$j]";
                $Subject="urlchecker: confusing response [$libr_name]";
                print MAIL "To: $mail_address\nFrom: $reply_to\nSubject: $Subject\n\n$email_body";
		close(MAIL);
	}
	if ($bad_url_txt[$j] ne ""){
		unless (open(MAIL,"|/usr/sbin/sendmail -t -bm")){
			print STDERR "**ERROR $0; couldn't register with email server. make sure that sendmail program is available.\n";
			exit 1;
		}
		$email_body="Ill-formed HTTP field:\n\n";
		$email_body.="$bad_url_txt[$j]";
                $Subject="urlchecker: bad URL [$libr_name]";
                print MAIL "To: $mail_address\nFrom: $reply_to\nSubject: $Subject\n\n$email_body";
		close(MAIL);
	}
}
closing($considered,$selected,$total_lines);
exit 0;
sub report_URL  {
 my ($title_key,$owning_libraries,$target,$body_text)=@_;
 my @libr;
 my $i;
	@libr=split(/ /,$owning_libraries);
	foreach $i (@libr){
		@$body_text[$i].="$target control_key: $title_key\n*****************\n";
	}
	return 0;
}
sub cleanup  {
}

sub exclude_them {
 my ($url_list,$outputf,$exception_file)=@_;
 my @exception_list;
 my $line;
 my $url;
 my $found;
 unless(open(EXCEPTIONS,"<",$exception_file)){
	print STDERR "$0: couldn't open exception file $exception_file\n";
	$outputf=$url_list;
	return 1;
 }
 @exception_list=<EXCEPTIONS>;
 close(EXCEPTIONS);
 unless(open(URL_LIST,"<",$url_list)){
	print STDERR "$0: couldn't open url list $url_list\n";
	return 1;
 }
 
 unless(open(OUT_LIST,">",$outputf)){
	print STDERR "$0: couldn't open output file $outputf\n";
	return 1;
 }
  while($line=<URL_LIST>){
	chomp($line);
	$found=0;
   CYCLE:  foreach $url (@exception_list){
			chomp($url);
			if ($url ne "" && $line=~m/$url/){
				 $found=1;
				last CYCLE;
			}
		}
		if ($found == 0){
			$status=print OUT_LIST "$line\n";
			if ($status == 0){
				print STDERR "$0: couldn't write to $outputf\n";
				return 1;
			}
		}
 }
 close(URL_LIST);
 close(OUT_LIST);
 return 0;
}

sub opening {
  use constant Sunday => "Sunday";
  use constant Monday => "Monday";
  use constant Tuesday => "Tuesday";
  use constant Wednesday => "Wednesday";
  use constant Thursday => "Thursday";
  use constant Friday => "Friday";
  use constant Saturday => "Saturday";
  use constant Jan => "Jan";
  use constant Feb => "Feb";
  use constant Mar => "Mar";
  use constant Apr => "Apr";
  use constant May => "May";
  use constant Jun => "Jun";
  use constant Jul => "Jul";
  use constant Aug => "Aug";
  use constant Sep => "Sep";
  use constant Oct => "Oct";
  use constant Nov => "Nov";
  use constant Dec => "Dec";
  my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime;
  my $thisday=(Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday)[$wday];
  my $thismon=(Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec)[$mon];
  my $thisyear=$year+1900;
  my $mins=sprintf("%02d",$min);
  my $secs=sprintf("%02d",$sec);
  my $hrs=sprintf("%02d",$hour);
  print STDERR "turbo_url started on $thisday, $thismon $mday, $thisyear, $hrs:$mins:$secs\n";
  return;
}
sub closing {
my ($considered,$selected,$processed)=@_;
## print STDERR "links considered:  $selected\n";
 print STDERR "links checked:  $processed\n";
  my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime;
  my $thisday=(Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday)[$wday];
  my $thismon=(Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec)[$mon];
  my $thisyear=$year+1900;
  my $mins=sprintf("%02d",$min);
  my $secs=sprintf("%02d",$sec);
  my $hrs=sprintf("%02d",$hour);
  print STDERR "turbo_url ended   on $thisday , $thismon $mday, $thisyear, $hrs:$mins:$secs\n";
 return;
}

sub check_print_recs {
my ($key,$field_856,$library,$skip_it,$selected)=@_;
my $i;
my $j;
my $uri;
my $found;
 	for ($i=0;$i<scalar(@$field_856);$i++){
		if ($$field_856[$i]=~m/\|u(.*?)\|/){
			$uri=$1;
			$found=0;
			for ($j=0;$j<scalar(@$skip_it);$j++){
				if ($uri =~ m/$$skip_it[$j]/){
					$found=1;
					last;
				}
			}
			if ($found == 0){
				$$selected++;
				print STDOUT "$uri|$key|$library|\n";
			}
		}
		elsif ($$field_856[$i]=~m/\|u(.*)/){
			$uri=$1;
			$found=0;
			for ($j=0;$j<scalar(@$skip_it);$j++){
 				if ($uri =~ m/$$skip_it[$j]/){
					$found=1;
					last;
				}
			}
			if ($found == 0){
				$$selected++;
				print STDOUT "$uri|$key|$library|\n";
			}
		}
		else{
			$$selected++;
			print STDOUT "|$key|$library|\n";
		}
 	}
}
sub give_help {
	print STDERR "  usage: turbo_url_alma.pl -i input-file \n       [-n threads] \n      -m mailing_list \n      -t tempdirectory \n      [-e exception-list]\n      [-d timer]\n";
	print STDERR "   input file is a text file with pipe-delimited fields. \n";
	print STDERR "     each input line is: url|mms_id|library_number(ignored). \n";
	print STDERR "   threads is the number of simultaneous url-checking processes. Default value is 4.\n";
	print STDERR "   mailing list is the file containing:\n    library-number|library-name|email_addresses|\n   threads is the number of simultaneous url-checking processes. Default value is 4.\n";
	print STDERR "   timer is the time-out value for the urlchecker. Default value is 20 seconds.\n";
	print STDERR "   exception list is the file containing the strings that should be ignored by turbo_url. One string per line.\n      For instance: www.ebsco.com means _ignore all URLs whose hostname is www.ebsco.com_\n";
	print STDERR "=======\n  turbo_url reads a text file that contains lines like:\nhttp://www.pitts.emory.edu/CDRI2/00002530.pdf|record_key|library_number|\n The pipe-delimited file is fed into the URL checker\n";
        return 0;
}
sub print_log {
}
