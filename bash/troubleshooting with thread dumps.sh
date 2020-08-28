# https://confluence.atlassian.com/confkb/troubleshooting-confluence-performance-issues-with-thread-dumps-688882387.html


# Find Application PID
APP_PID=`ps aux | grep -i APP_NAME | grep -i java | awk  -F '[ ]*' '{print $2}'`

# The script will generate 6 sets of CPU usage info and thread dumps at 10 seconds intervals, running for a total of 60 seconds
for i in $(seq 6); 
	do 
		top -b -H -p $APP_PID -n 1 > app_cpu_usage.`date +%s`.txt; 
		jstack $APP_PID > app_threads.`date +%s`.txt; 
		sleep 10; 
	done

# these scripts do the same, however they assume that is the only one Java application on the host
for i in $(seq 6); 
	do 
		top -b -H -p `ps -ef | grep java | awk 'FNR == 1 {print $2}'` -n 1 > app_cpu_usage.`date +%s`.txt;
		jstack `ps -ef | grep java | awk 'FNR == 1 {print $2}'` > app_threads.`date +%s`.txt;
		sleep 10;
	done


for i in $(seq 6);
	do
		top -b -H -p `pgrep -f java` -n 1 > app_cpu_usage.`date +%s`.txt;
		jstack `pgrep -f java` > app_threads.`date +%s`.txt;
		sleep 10;
	done
