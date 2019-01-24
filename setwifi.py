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