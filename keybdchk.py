# Copyright (c) 2018 HIE of One, PBC
# Author: Adrian Gropper
# with thanks to Adafruit Industries for their inspiration, support, education and the SSD1306 drivers
# This is licensed as Free software under the GNU Affero General Public License

import evdev
import re

def keybd():
	keyboards = {}							# Need at least one keyboard to scroll SSID and enter a password
	devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
	for device in devices:
#		print(device.path, device.name, device.phys)		# Useful for debugging new devices
		getcaps = str(device.capabilities(verbose=True))
		if re.search('KEY_ESC', getcaps):					# Assume that only keyboards have an Esc key
			keyboards[device.path] = device.name     
#			print 'Got ', len(keyboards), 'Keyboards: ', keyboards
			thedevice = device.path							# Use path as the index since names could be random
	for keyboard in keyboards:								# Favor hardwired keyboards
		if keyboards.get(keyboard) != 'Bluetooth Keyboard': thedevice = keyboard		# Favor hardwired keyboards
	try:
		device = evdev.InputDevice(thedevice)
#		print(device)
		kbd = True				# Probably true, but BT keyboards often disconnect after some minutes
	except:
		kbd = False
		device = ''
	return (kbd, device)
