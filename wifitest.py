# Copyright (c) 2018 HIE of One, PBC
# Author: Adrian Gropper
# with thanks to Adafruit Industries for their inspiration, support, education and the SSD1306 drivers
# This is licensed as Free software under the GNU Affero General Public License

# List the available connections 
# much of this is from http://faradaysclub.com/?p=1016

from subprocess import check_output
import csv
import time

#get the current time to name a file later on
timestamp = time.strftime("%m-%d-%Y-%I:%M:%S")

#define a function for doing a wifi scan
def wifiscan():
  ssid = []
  scanoutput = check_output(["iwlist", "wlan0", "scan"])
  curtime = time.strftime("%I:%M:%S")
  ssid.append(curtime)

  for line in scanoutput.split():
    line=str(line)
    if line.startswith("ESSID"):
		  line=line[7:-1]
		  ssid.append(line)
  with open('/home/pi/wifi/'+timestamp+'.csv','a') as csvfile:
      csvwriter = csv.writer(csvfile,delimiter=',')
      csvwriter.writerow(ssid)
#  print ssid
  return ssid

  
#ssid = wifiscan()
#return ssid
  
  