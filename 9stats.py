# Copyright (c) 2018 HIE of One, PBC
# Author: Adrian Gropper
# with thanks to Adafruit Industries for their inspiration, support, education and the SSD1306 drivers
# This is licensed as Free software under the GNU Affero General Public License

# Warning
#					This is a daemon that starts automatically along with a demo webserver
#					The daemon listens to your keyboard whether you can see the python display or not 
#					and it will execute your keystrokes including triggering a Reboot.
#					You must:        sudo systemctl stop trustee.service     before anything else.


import subprocess		# Used to check for IP address
import keytostr			# The routines that process keystrokes into a useful string
import time
import re				# To parse the keyboard or mouse device properties

# Scan SSID and log to /home/pi/wifi/'+timestamp+'.csv','a') as csvfile
import wifitest
import setwifi
import os				# for the reboot after wifi connect
import evdev
import keybdchk			# to look for a connected keyboard
#						First we check our wifi and IP connectivity
ssid = wifitest.wifiscan()
ssid.pop(0)					# remove the time
ssid.append('anotherwifi2')							 # just to test
nextssid = 0				# left or right arrow
got = str(len(ssid))		# used by the prompt message
print got, ' SSID ', ssid

# Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
cmd = "hostname -I | cut -d\' \' -f1"
IP = subprocess.check_output(cmd, shell = True )

if len(IP) > 7:					# Don't prompt for a scan if you already have an IP
	prompt0 = 'http://' + str(IP)
	prompt1 = 'Type Enter to Rescan'
	prompt3 = ''
	nextEnter = 'Confirm Rescan?'
else:
	prompt0 = got + ' WiFi... Use < or >'		# This is the initial prompt on the line [0]
	prompt1 = 'Type Pass: and Enter'			# This is the initial prompt on the line [1]
	prompt3 = 'Pass: '							# Prompt for the (wifi) password
	nextEnter = 'Confirm blank'
	print nextEnter
prompt2 = 'WiFi: '
keystr = ''   								# This is the initial keyboard string where a password might appear
cmd = ''									# This is the command triggered by Enter

# Start a web server as a separate httpd.service - to be replaced by Trustee

# AG from https://python-evdev.readthedocs.io/en/latest/usage.html
#
#   Bluetooth keyboards are always fussy to use because they disconnect if not used for a bit.
#   The real-time loop must catch and handle keyboard exceptions,
#     prompt the user that a kbd is missing and poll the device driver until it reappears.
#   The kbd status code will need to be cleaned up: 
#		 Miss should just track seconds since we saw a kbd event so we suspect disconnection
#        _MISS should be a constant set according to the Raspi BT timeout, whatever it is
_MISS = 5 # The pi Zero clock seems to run at 1/5 real time. 20 is actually more like 100 seconds
			# The real time loop seems to be about one second in real time.
#	A future enhancement would replace the time() clock with hardware timestamps of key events in evdev

kbd, device = keybdchk.keybd()		
miss = 0					# How many seconds since we saw a keyboard event - could mean disconnection
elapt = time.time()

# Cursor and string input stuff
# New text lines will be addressed from the bottom up by the cursor Y - the lowest line is currently 3
# The 128 x 64 display uses
_FONTH = 9					# # Assume a 6x8 font with no pixel on either side of the letter but 1 pixel for cursor
#txt = [ 32, 42, 52, 62 ]
#_HOMER = 62 				# The home row for the cursor (char paints at 45 + 8 + 1 to put cursor below g vs.q)
#
txt = [ 8, 16, 24, 31 ]
_HOMER = 32 				# The home row for the cursor (char paints at 45 + 8 + 1 to put cursor below g vs.q)
cy = _HOMER					# 62 is the last cy that shows the cursor. That's 64 + a padding of -2 for whatever reason

_CURW = 6					# Assume a 6x8 font with no pixel on either side of the letter
_HOMEC = 0					# The leftmost position
cx = _HOMEC
cindex = 0					# The cursor position within the displayed keystr

# AG commented out the Adafruit SPI stuff
import RPi.GPIO as GPIO
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
#disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# First define some constants to allow easy resizing of shapes.
padding = -2		# was -2 for some reason AG: apparently draw.text takes a Y that's 2 pixels above draw.line' Y
top = padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

# From here down, we run a real time executive loop. Catching ^C is for cleanup, if needed.
# The loop starts with:
#	- processing of user input events, 
#	- ending with a rather slow I2C display update
#	- and a sleep() to give other software a chance to run

shifted = False						# Assume the shift key is up (but all keys are reported as CAPS by default)
try:
	while True:

		draw.rectangle((0,0,width,height), outline=0, fill=0) 			# Draw a black filled box to clear the image.
		# Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
#		cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
#		Disk = subprocess.check_output(cmd, shell = True )
								
# AG added
		if kbd:											# if you think there's no keyboard, don't look for keys
			i = 30										# drain up to 30 events
			while i > 0:
				try:									# will need try for when BT device goes away
					event = device.read_one()
					if event == None:
						break
					if event.type == evdev.ecodes.EV_KEY:
						elapt = time.time() 				# a key event is always reassuring
						ev = repr(evdev.categorize(event))  # parse
						evl = ev.split(",")                 # skip to key[3] and state[4]

						if (' 42' in evl[3] or ' 54' in evl[3]):    # Shift
							if ' 1L' in evl[4]:	shifted = True		# key down								
							if ' 2L' in evl[4]: pass				# hold
							if ' 0L' in evl[4]: shifted = False		# key Up
#							print 'Shifted ', shifted, 'key ',

						elif ' 1L' in evl[4]: 				# look only for Key Down
							ckey = evdev.ecodes.KEY[int(evl[3])]
							key = ckey.split("_")[1]		# strip the 'KEY_'
							if not shifted:					# what's left is Capitalized by default
								key = str.lower(key)		# doesn't work for symbols
#							print 'Shifted ', shifted, 'key ', key

# Four command keys are currently defined: enter, right, and left
							if key == 'enter':			# A command! Time to do something!
								cmd = nextEnter
								break					# Don't update the input string
							if key == 'esc':			
								cmd = 'esc'
								break
							if key == 'right':			# these the scroll WiFi keys
								nextssid += 1
								if nextssid > len(ssid)-1: nextssid = 0  # with wrap around
								break
							if key == 'left':			
								nextssid -= 1
								if nextssid < 0: nextssid = len(ssid)-1
								break
# Otherwise, not a command so update the keyboard input string
							keystr, cindex, cx = keytostr.dokey(keystr, key, cindex, cx)

						if ' 2L' in evl[4]: 				# look only for hold
							print '.',
				except:
					pass				
				i = i - 1           #  End of while trying to get some events - 30 times 

# Enter processing below			
			if cmd == 'Confirm Rescan?':			# You're here because you already have an IP	
				cmd = ''	
				prompt1 = 'Enter again to rescan'	# Ask for another Enter
				nextEnter = 'Confirm blank'
				prompt0 = got + ' WiFi... Use < or >'		# This is the initial prompt on the line [0]
				prompt1 = 'Type Pass: and Enter'			# This is the initial prompt on the line [1]
				prompt2 = 'WiFi: '
				prompt3 = 'Pass: '							# Prompt for the (wifi) password
				keystr = ''   			# This is the initial keyboard string where a password might appear
				cindex = 0
				cx = 0
				print nextEnter + ' with password ' + keystr
			elif cmd == 'Confirm blank':
				print 'cmd = ' + cmd + ' about to check for blank password'  
				cmd = ''	
				passwd = keystr		#save the password
				print ("Confirm blank on " + passwd + ' password')
				if passwd == '':
					print 'Really enter a blank password?'
					prompt0 = 'Enter a blank passwd?'
					prompt1 = '  or Esc to Cancel'
					nextEnter = 'Reboot'
				else:
					setwifi.setsupplicant(ssid[nextssid], passwd)  # writes the file

					prompt0 = 'Rebooting...'
					prompt2 = '...for up to 3 min.'
					draw.rectangle((0,0,width,height), outline=0, fill=0)			# erase
					draw.text((x, txt[0]-10),    prompt0,  font=font, fill=255)
					draw.text((x, txt[2]-10),    prompt2,  font=font, fill=255)
					disp.image(image)			# This adds 0.09 seconds
					disp.display()				# This adds 0.04 seconds
					time.sleep(.2)
					print 'Hit ^C immediately to quit without rebooting'
					time.sleep (10)
#					while True:
#						pass
					GPIO.cleanup()
					os.system('sudo shutdown -r now') 
					
			elif cmd == 'Reboot': 
			
				setwifi.setsupplicant(ssid[nextssid], passwd)  # writes the file

				prompt0 = 'Rebooting...'
				prompt2 = '...for up to 3 min.'
				draw.rectangle((0,0,width,height), outline=0, fill=0)			# erase
				draw.text((x, txt[0]-10),    prompt0,  font=font, fill=255)
				draw.text((x, txt[2]-10),    prompt2,  font=font, fill=255)
				disp.image(image)			# This adds 0.09 seconds
				disp.display()				# This adds 0.04 seconds
				time.sleep(.2)
				print 'Hit ^C immediately to quit without rebooting'
				time.sleep(10)
#				while True:
#					pass
				GPIO.cleanup()
				os.system('sudo shutdown -r now') 
			elif cmd == 'esc':
				cmd = ''
				key = ''									# swallow the key too
				keystr = ''								# clear the line[3] string
				prompt3 = ''
				cindex = 0
				cx = 0
				prompt0 = 'http://' + str(IP)
				prompt1 = 'Type Enter to Rescan'
				nextEnter = 'Confirm Rescan?'
#				print 'Esc in Confirm Rescan to ' + nextEnter + 'with cindex = ', cindex, cx
			else:
				pass

			# At this point we're connected and in an idle loop			
				
			# No event could mean the BT keyboard is disconnected 
			miss = int(time.time() - elapt)
			if miss > _MISS:								# Warn the user and try to reconnect
				kbd, device = keybdchk.keybd()				# Verify keyboard again after many seconds of inactivity
#				print 'Keyboard may be ', kbd, ' for ', miss, ' seconds'
				elapt = time.time()
		#  End of kbd True
		else:												# Keyboard is disconnected			
			miss = int(time.time() - elapt)				
#			print "Keyboard missing!", miss, " sec"
			kbd, device = keybdchk.keybd()
			if kbd:	elapt = time.time()						# Keyboard is back, reset the time elapsed since the kbd was seen
 
		# End of keyboard activity section		
		#  Display 4 lines and the cursor
		draw.text((x, txt[0]-10),    prompt0,  font=font, fill=255)
		draw.text((x, txt[1]-10),    prompt1,  font=font, fill=255)
		draw.text((x, txt[2]-10),    prompt2 + ssid[nextssid],  font=font, fill=255)
		if kbd:																			# all typing is on the last line
			draw.text((x, txt[3]-10),    prompt3 + keystr,  font=font, fill=255)		
			draw.line([(cx + (_CURW * len(prompt3)), txt[3]), (cx + (_CURW * len(prompt3))+_CURW, txt[3])], fill=255)		# http://effbot.org/imagingbook/imagedraw.htm
		else:
			draw.text((x, txt[3]-10),    "   Keyboard missing!",  font=font, fill=255)
		# Display image.
		disp.image(image)			# This adds 0.09 seconds
		disp.display()				# This adds 0.04 seconds
			
		time.sleep(.1)

# End of real time executive loop
	
except KeyboardInterrupt: 
    GPIO.cleanup()
