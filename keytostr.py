# Copyright (c) 2018 HIE of One, PBC
# Author: Adrian Gropper
# with thanks to Adafruit Industries for their inspiration, support, education and the SSD1306 drivers
# This is licensed as Free software under the GNU Affero General Public License

# AG simple input string handling routines
#
# Ref: https://developers.google.com/edu/python/dict-files
#
kmap = {}				# always returns a single char
kmap['space']	= ' '
kmap['dot']		= '.'
kmap['grave'] = '`'
kmap['GRAVE'] = '~'
kmap['minus'] = '-'
kmap['MINUS'] = '_'
kmap['equal'] = '='
kmap['EQUAL'] = '+'
kmap['tab'] = ' '
kmap['TAB'] = ' '
kmap['leftbrace'] = '['
kmap['LEFTBRACE'] = '{'
kmap['rightbrace'] = ']'
kmap['RIGHTBRACE'] = '}'
kmap['comma'] = ','
kmap['COMMA'] = '<'
kmap['DOT'] = '>'
kmap['slash'] = '/'
kmap['SLASH'] = '?'
kmap['leftmeta'] = ' '
kmap['LEFTMETA'] = ' '
kmap['SPACE'] = ' '
kmap['leftctrl'] = ' '
kmap['LEFTCTRL'] = ' '
kmap['leftmeta'] = ' '
kmap['LEFTMETA'] = ' '
kmap['leftalt'] = ' '
kmap['LEFTALT'] = ' '
kmap['rightalt'] = ' '
kmap['RIGHTALT'] = ' '
kmap['rightmeta'] = ' '
kmap['RIGHTMETA'] = ' '
kmap['rightctrl'] = ' '
kmap['RIGHTCTRL'] = ' '
kmap['up'] = ' '
kmap['down'] = ' '
kmap['volumedown'] = ' '
kmap['volumeup'] = ' '
kmap['previoussong'] = ' '
kmap['playpause'] = ' '
kmap['nextsong'] = ' '
kmap['search'] = ' '
kmap['homepage'] = ' '
kmap['semicolon'] = ';'
kmap['SEMICOLON'] = ':'
kmap['apostrophe'] = '\''
kmap['APOSTROPHE'] = '"'
kmap['backslash'] = '\\'
kmap['BACKSLASH'] = '|'
kmap['capslock'] = ' '
kmap['CAPSLOCK'] = ' '

_CURW = 6   # Careful, this cursor width is also defined in the calling routine

def dokey(keystring, key, cindex, cx):
# backspace needs to index 
	if key == 'backspace':
		if cindex:
			cindex -= 1
			cx = cindex * _CURW
			keystring = keystring[:-1]
		return keystring, cindex, cx
# this will need a table of keynames to chars
	elif kmap.get(key):
		key = kmap.get(key)
	else:
		if len(key) > 1:
			print (key, " not in dictionary")
			f = open('/home/pi/wifi/keymap.txt', 'a')		# use this to update the dictionary
			addone = 'kmap[\'' + key + "\'] = \' \'\n"
			f.write(addone)
			key = '?'					# dictionary lookup failed
				
# most keys are reported as a single, capital letter 
	keystring = keystring + ' '		# provisionally extend the string
	l = list(keystring)     		# split string in array
	l[cindex] = key					# add the key to the array
	keystring = "".join(l)
	cindex += 1						# and move the cursor
	cx = cindex * _CURW
	return keystring, cindex, cx
