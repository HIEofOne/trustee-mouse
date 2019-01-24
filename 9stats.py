# Copyright (c) 2018 HIE of One, PBC
# Author: Adrian Gropper
# with thanks to Adafruit Industries for their inspiration, support, and education and the SSD1306 drivers.
# See https://github.com/adafruit/Adafruit_Python_SSD1306/blob/master/examples/animate.py and stats for roots.

# WARNING			This is a daemon that starts automatically along with a demo webserver
#					The daemon listens to your keyboard whether you can see the python display or not 
#					and it will execute your keystrokes including triggering a Reboot.
#					You MUST:        sudo systemctl stop trustee.service     before anything else.
#					https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units

# Also, separately, start web app daemon as a separate httpd.service - to be replaced by full Trustee code

def cursx(keystring, Font):												# Calculate the cursor start point for TT fonts
	px = 0
	for c in keystring:
		char_width, char_height = draw.textsize(c, font=Font)
		px += char_width
	return px

def	display4(erase, state, parm0, parm2, parm3, seconds):				# displays 4 lines per the state
	global prompt3														# to position the cursor
	if state[2] == '< Scroll WiFis >': 									# The display state depends on what SSID in ssid is shown					
		if nextssid == 0 and ssid[0] == 'Enter WiFi name':				# ssid[0] has not yet been updated by the user
			state = getState('EnterHidden')				# NOTE: This is a display enhancement here, the actual state is still NotConnPwd
			parm0 = ''													# When enter is done, the test will need to be repeated
		else:
			state = getState('NotConnPwd')
			parm0 = got
	prompt3 = state[4]
	if prompt3:									# If there's a prompt at all, should it be Pwd: or WiFi:?
		if nextssid == 0 and ssid[0] == 'Enter WiFi name':   # ssid[0] has not yet been updated by the user
			prompt3 = 'WiFi: '
		else:
			prompt3 = 'Pwd: '
		
	if erase == 'Clr': draw.rectangle((0,0,width,height), outline=0, fill=0)			# erase
	if state[0] == 'NotConnPwd':
		draw.text((0, txt[0]),    state[1] + parm0 + '  WiFis',  font=Font, fill=255)	# insert the parameter 
	else:
		draw.text((0, txt[0]),    state[1] + parm0,  font=Font, fill=255)				# append the parameter 	
	draw.text((0, txt[1]),    state[2],  font=Font, fill=255)
	draw.text((0, txt[2]),    state[3] + parm2,  font=Font, fill=255)
	draw.text((0, txt[3]),    prompt3 + parm3,  font=Font, fill=255)
	disp.image(image)
	disp.display()
	time.sleep(seconds)
	return state[5], state[6]

def getState(state):		# peels off one state list from the state table
	for S in lol:
		if S[0] == state: 
			return S


import subprocess			# Used to check for IP address
import keytostr				# The routines that process keystrokes into a useful string
import time
import re					# To parse the keyboard or mouse device properties


import wifitest				# Will scan SSID and log to /home/pi/wifi/'+timestamp+'.csv','a') as csvfile
import setwifi				# Write a supplicant.conf file per https://www.raspberrypi.org/forums/viewtopic.php?t=203716
import os					# for the reboot after wifi connect
import evdev				# for keyboard events
import keybdchk				# to look for a connected keyboard

import RPi.GPIO as GPIO		# GPIO pins are used by display driver reset but not relevant to I2C
import Adafruit_SSD1306

from PIL import Image, ImageDraw, ImageFont

# Display Initializations
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)		# # 128x64 display with hardware I2C (On the PiOLED RST pin isnt used)
disp.begin()											# Initialize library.
disp.clear()											# Clear display.
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))					# Create blank image for drawing. Make sure to create image with mode '1' for 1-bit color.
draw = ImageDraw.Draw(image)							# Get drawing object to draw on image.

# Font, cursor, and string input stuff
					# font = ImageFont.load_default() # Load default font.
					# Alternatively load a TTF font.  Make sure the .ttf font file path is complete so it works as a systemd service
Font = ImageFont.truetype('/home/pi/Trustee/runescape_uf.ttf', 16) # +3 This is NOT a monospaced font
					# Some other nice fonts to try: http://www.dafont.com/bitmap.php
					# font = ImageFont.truetype('PIXEARG_.TTF', 8) # +2 (nice and small width)
					# font = ImageFont.truetype('MotorolaScreentype.ttf', 14) # +2

_CURW = 6										# Default cursor width, will be adjusted to the actual char size 
cindex = 0										# The cursor position within the displayed keystr

txt = [0, 16, 34, 48 ]							# Line spacing 
cy = 63											# 63 is the last row and it shows the cursor. All typing is done in the last row.

# Construct the state table 
# State	S		prompt0					prompt1					prompt2					prompt3			Enter to:		Esc does	
lol=[
['Started',		'Welcome to Trustee',   '',						'Checking for network', '', 			'Scanning', 	''],
['Connected', 	'http://',				'Enter to rescan',		'WiFi: ',				'',				'Scanning',		''],	
['Scanning', 	'Scanning for WiFi',	'',						'',						'',				'NotConnPwd',	''],
['NotConnPwd',	'Found  ',				'< Scroll WiFis >',		'WiFi: ',				'Pwd: ',		'TestEmptyStr',	'Scanning'],
['EnterHidden', 'Enter hidden WiFi',	'< Scroll WiFis >',		'',						'WiFi: ',		'TestEmptyWif',	'Scanning'],
['FoundNoWiFi', 'Found no WiFi',		'Esc to rescan',		'WiFi: ',				'WiFi: ',		'TestEmptyWif',	'Scanning'],
['TestEmptyStr', 'Blank Password? ',	'Esc to cancel',		'WiFi: ',				'Pwd: ',		'RebootingIn',	'NotConnPwd'],
['TestEmptyWif', 'Need a WiFi name',	'',						'WiFi: ',				'WiFi: ',		'NotConnPwd',	'Scanning'],
['RebootingIn', 'Rebooting in ',		'Esc to cancel',		'WiFi: ',				'Pwd: ',		'Rebooting',	'Scanning'],
['Rebooting',	'Rebooting......',		'Could take 2 minutes',	'',						'',				'Rebooting',	''],
['CyclePower',	'Trustee not running',	'Unplug then replug',	'to restart',			'',				'Rebooting',	''],
]
# Add commands to set pi password here

S = getState('Started')
nextEnter, nextEsc = display4('Clr', S, '', '', '', 3)	# the state is returned as a string

# If we have a working Ethernet connection, the keyboard stuff is completely optional

cmd = "hostname -I | cut -d\' \' -f1" 			# See: https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
IP = subprocess.check_output(cmd, shell = True )

ssid = ['Enter WiFi name']								# ssid[0] is reserved for entering a hidden WiFi SSID
nextssid = 0										
if len(IP) > 7:											# Don't prompt for a scan if you already have an IP
	S = getState('Connected')
	param0 = str(IP)									# Needed in the keyboard loop
	try:
		for line in open('/etc/wpa_supplicant/wpa_supplicant.conf','r'):
			if "ssid" in line:
				ssid.append(line.split('\"')[1])		# in rare cases there's more than one in the file
				nextssid = len(ssid)-1
				print 'Wifi SSID: ', ssid[nextssid]
	except:
		print 'No wpa_supplicant file found.'
else:
	S = getState('Scanning')
	param0 = ''


keystr = ''   											# This is the initial keyboard string where a password might appear
cmd = S[0]												# This is the current state
lastS = cmd												# This is used to print state changes to the console
print 'Entering keyboard loop in state: ', lastS


# AG from https://python-evdev.readthedocs.io/en/latest/usage.html
#   Bluetooth keyboards are always fussy to use because they disconnect if not used for a bit.
#   The real-time loop must catch and handle keyboard exceptions,
#     prompt the user that a kbd is missing and poll the device driver until it reappears.
#   Miss should just track seconds since we saw a kbd event so we suspect disconnection      
_MISS = 5 												# _MISS should be a constant set according to the Raspi BT timeout, whatever it is
kbd, device = keybdchk.keybd()		
miss = 0												# How many seconds since we saw a keyboard event - could mean disconnection
elapt = time.time()


# From here down, we run a real time executive loop. Catching ^C is for cleanup, if needed.
							# The loop starts with:
							#	- processing of user input events, including Shift and separation of command strokes
							#   - Only Enter and Escape can trigger a one-time cmd and change the state machine S
							#   - Command processing initiated by a keystroke happens next
							#   - Followed by commands that happen without a keystroke
							#	- ending with a rather slow I2C display update
							#	- and a sleep() to give other software a chance to run

shifted = False														# Assume the shift key is up (but all keys are reported as CAPS by default)
try:
	while True:

		if kbd:														# if you think there's no keyboard, don't look for keys
			i = 30													# drain up to 30 events
			while i > 0:
				try:												# will need try for when BT device goes away
					event = device.read_one()
					if event == None:
						break
					if event.type == evdev.ecodes.EV_KEY:
						elapt = time.time() 						# a key event is always reassuring
						ev = repr(evdev.categorize(event)) 			# parse
						evl = ev.split(",")                 		# skip to key[3] and state[4]

						if (' 42' in evl[3] or ' 54' in evl[3]):    # Shift
							if ' 1L' in evl[4]:	shifted = True		# key down								
							if ' 2L' in evl[4]: pass				# hold
							if ' 0L' in evl[4]: shifted = False		# key Up

						elif ' 1L' in evl[4]: 						# look only for Key Down
							ckey = evdev.ecodes.KEY[int(evl[3])]
							key = ckey.split("_")[1]				# strip the 'KEY_'
							if not shifted:							# what's left is Capitalized by default
								key = str.lower(key)				# doesn't work for symbols

# Four command keys are currently defined: enter, escape, right, and left
							if key == 'enter':						# A command! This changes the state and the display
								nextEnter, nextEsc = display4('Clr', S, '', '', '', 0)
								cmd = nextEnter
								if lastS == 'TestEmptyStr' and cmd == 'RebootingIn':
									param0 = str(10)				# Initialize the Rebooting countdown
								print '* Going from ', lastS, ' to ', cmd
								lastS = cmd
								S = getState(S[5])					# Advance the state - always
								break								# Don't update the input string
							if key == 'esc':						# No matter what, clear the input string
								key = ''							# swallow the key too
								keystr = ''							# clear the line[3] string
								cindex = 0							# return the cursor to leftmost
								nextEnter, nextEsc = display4('Clr', S, '', '', '', 0)
								if nextEsc: 
									cmd = nextEsc
									print '*** Going from ', lastS, ' to ', cmd
									lastS = cmd
									S = getState(S[6])				# Advance the state - always
								break
							if key == 'right':						# these the scroll WiFi keys, they almost never change the state 
								nextssid += 1						# unless the state displayed is the "Enter Hidden WiFi SSID" state 
								if nextssid > len(ssid)-1: nextssid = 0  # with wrap around
								keystr = ''
								cindex = 0
								break
							if key == 'left':			
								nextssid -= 1
								if nextssid < 0: nextssid = len(ssid)-1
								keystr = ''
								cindex = 0
								break
# Otherwise, not a command so update the keyboard input string
							keystr, cindex = keytostr.dokey(keystr, key, shifted, cindex)
#							print '    keystr = ' + keystr, 'State S = ' + S[0]
						if ' 2L' in evl[4]: 						# look only for hold
							print '.',
				except:
					pass				
				i = i - 1           								#  End of while trying to get some events - 30 times 

# Enter (command) processing below			
			if cmd == 'Scanning':									# You may or may not already have an IP	
				display4('Clr', S, '', '', '', 0)
				cmd = ''											# Clear the command selector until next enter or something
				ssid = wifitest.wifiscan()							# Check our wifi and IP connectivity - could be an empty list
				got = str(len(ssid) - 1) 							# used by the prompt message
				print 'Found ', got, ' SSID ', ssid					# Sometimes it finds 0 because of a system error - S undefined err on line 262
				if int(got) > 0:									# Did we find at least one WiFi?
					S = getState(S[5])								# Advance the state after the scan even though there was no Enter
					param0 = got
					nextssid = 1									# first should be strongest, left or right arrow will change this
				else:
					S = getState('FoundNoWiFi')						# This state does not offer to scroll WiFis - all you can do is enter a name
					param0 = ''
					nextssid = 0									# Display the prompt									
				nextEnter, nextEsc = display4('Clr', S, '', '', '', 0)		# Update the display and the state
				print '** Going from ', lastS, ' to ', S[0]
				lastS = S[0]
			elif cmd == 'NotConnPwd':
				cmd = ''
				param0 = got										# Restore the Found parameter
			elif cmd == 'TestEmptyStr':								# Require an extra Enter if the password is empty
				cmd = ''
				param0 = ''
				if keystr:
					S = getState('RebootingIn')						# Advance the state to RebootingIn without waiting for Enter
					param0 = str(10)
 				print 'Test password string ', keystr, 'Going to S = ', S[0]	# to RebootingIn, which doesn't need a keystroke
				passwd = keystr
			elif cmd == 'TestEmptyWif':
				cmd = ''
				if keystr:
					ssid[0] = keystr								# Replace the prompt with the actual name
					S = getState('NotConnPwd')						# Advance the state to NotConnPwd
					keystr = ''
					cindex = 0
 				else:
 					ssid[0] = 'Enter WiFi name'						# Can't proceed without a real SSID, back to default
 					S = getState('TestEmptyWif')					# so ask again
 					param0 = ''	
 				print 'Test SSID string ', ssid[0], 'Going to S = ', S[0]
			else:
				pass
				
		# No event could mean the keyboard is disconnected 
			miss = int(time.time() - elapt)
			if miss > _MISS:										# Warn the user and try to reconnect
				kbd, device = keybdchk.keybd()						# Verify keyboard again after many seconds of inactivity
				elapt = time.time()
		#  End of kbd True
		else:														# Keyboard is disconnected			
			miss = int(time.time() - elapt)				
			kbd, device = keybdchk.keybd()
			if kbd:	elapt = time.time()								# Keyboard is back, reset the time elapsed since the kbd was seen
 		# End of keyboard activity section		

#  Some state changes are not triggered by a keystroke at all
		if S[0] == 'RebootingIn':									# Notice that this command does not clear itself yet
			print 'Rebooting In ', param0, ' seconds'
			if param0 == '0': 
				S = getState(S[5])
			else:
				x = int(param0) - 1
				param0 = str(x)
				time.sleep(1)
		elif S[0] == 'Rebooting': 			
			setwifi.setsupplicant(ssid[nextssid], passwd)  			# writes the file
			time.sleep(.2)
			print 'Hit ^C immediately to quit without rebooting'
			time.sleep(5)
			GPIO.cleanup()
			os.system('sudo shutdown -r now') 

		param2 = ssid[nextssid]

#  Display 4 lines and the cursor without changing the state
		if S[0] != lastS:
			print 'Going from ', lastS, ' to ', S[0]
			lastS = S[0]
		if kbd:														# all typing is on the last line
			display4('Clr', S, param0, param2, keystr, 0)		
			px = cursx(keystr, Font)
			draw.line([(px + cursx(prompt3, Font), cy), (px + cursx(prompt3, Font) +_CURW, cy)], fill=255)		# http://effbot.org/imagingbook/imagedraw.htm
			disp.image(image)										# update to add the cursor
			disp.display()
		else:
			display4('Clr', S, param0, param2, ' Keyboard Missing!', 0)

		time.sleep(.1)
#  End of real time executive loop
	
except KeyboardInterrupt: 
    GPIO.cleanup()
