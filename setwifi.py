# Copyright (c) 2018 HIE of One, PBC
# Author: Adrian Gropper
# with thanks to Adafruit Industries for their inspiration, support, education and the SSD1306 drivers
# This is licensed as Free software under the GNU Affero General Public License

# Write a supplicant.conf file per https://www.raspberrypi.org/forums/viewtopic.php?t=203716

def setsupplicant(ssid, passwd):
	fh = open('/etc/wpa_supplicant/'+'wpa_supplicant'+'.conf','w')
	fh.writelines('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
	fh.writelines('update_config=1\n')
	fh.writelines('country=US\n')
	fh.writelines('\n')
	fh.writelines('network={\n')
	fh.writelines('     ssid="'+ssid +'"\n')
	fh.writelines('     psk="'+passwd +'"\n')
	fh.writelines('     key_mgmt=WPA-PSK\n')
	fh.writelines('}\n')
	fh.close()
	return		