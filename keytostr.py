# AG simple input string handling routines
#
# Ref: https://developers.google.com/edu/python/dict-files
#

from PIL import ImageFont
from PIL import ImageDraw

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
kmap['1S'] = '!'
kmap['2S'] = '@'
kmap['3S'] = '#'
kmap['4S'] = '$'
kmap['5S'] = '%'
kmap['6S'] = '^'
kmap['7S'] = '&'
kmap['8S'] = '*'
kmap['9S'] = '('
kmap['0S'] = ')'


def dokey(keystring, key, shifted, cindex):
	
# backspace needs to index 
#	print ' in keytostr ', key, shifted
	if shifted and len(key) == 1:							# this is a number key
		key = key + 'S'										# and it needs mapping
	if key == 'backspace':
		if cindex:
			cindex -= 1
			keystring = keystring[:-1]
		return keystring, cindex
# this will need a table of keynames to chars
	elif kmap.get(key):
		key = kmap.get(key)
	else:
		if len(key) > 1:									# most keys are reported as a single, capital letter 
			print (key, " not in dictionary")
			f = open('/home/pi/wifi/keymap.txt', 'a')		# use this file to update the dictionary
			addone = 'kmap[\'' + key + "\'] = \' \'\n"
			f.write(addone)
			key = '?'					# dictionary lookup failed
				
# most keys are reported as a single, capital letter 
	keystring = keystring + ' '		# provisionally extend the string
	l = list(keystring)     		# split string in array
	l[cindex] = key					# add the key to the array
	keystring = "".join(l)
#	print keystring, cindex
	cindex += 1						# and move the cursor
	
	return keystring, cindex
