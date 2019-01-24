# List the available connections 
# from http://faradaysclub.com/?p=1016
from subprocess import check_output
import csv
import time

#get the current time to name a file later on
timestamp = time.strftime("%m-%d-%Y-%I:%M:%S")

#define a function for doing a wifi scan
def wifiscan():
	ssid = ['Enter WiFi name']									# ssid[0] is reserved for entering a hidden WiFi SSID
	try:
		scanoutput = check_output(["iwlist", "wlan0", "scan"])
	except:														# returns empty ssid array if wlan0 throws an error
		print 'In wifiscan: wlan0 error'
#		ssid.append = 'wlan error'
		return ssid												# there's no log entry in the timestamped file - should be improved
	curtime = time.strftime("%I:%M:%S")
	ssid.append(curtime)
	i = 0	
#	in_ESSID = False												# count lines until next "\""
	for line in scanoutput.split():
		line=str(line)
		if line.startswith("ESSID"):
			i = 6
			s = ''
			s = line[7:]
#			line=line[7:-1]
#			ssid.append(line)
		if i > 0:
			i -= 1
			s = s + ' ' + line
			if line[-1] == "\"":
				i = 0
#				s = s[7:-1]
				t = s.split("\"")
				s = t[len(t)-2]
				ssid.append(s)
				print ssid

	with open('/home/pi/wifi/'+timestamp+'.csv','a') as csvfile:
		csvwriter = csv.writer(csvfile,delimiter=',')
		csvwriter.writerow(ssid)
#  print ssid
	ssid.pop(1)									# remove the time before returning
	return ssid
  
  