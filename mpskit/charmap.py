import sys
import os.path
import json
from mpskit.record import Record
from mpskit.conf import conf
from mpskit.fail import fail,warning,printf

# NOTE: charmap will not be applied to "[]" characters and everything inside them
# NOTE: charmap: keep lower and upper case characters separated by 32
# NOTE: charmap: keep digits at their default positions
# NOTE: charmap: keep 010, 013 codes (line-feed and carriage-return)
# NOTE: charmap: in Rex keep "@"

default_charmap = u'''{
"000": "|",
"010": "\\u000A",
"013": "\\u000D",
"064": "@",
"048": "0",
"049": "1",
"050": "2",
"051": "3",
"052": "4",
"053": "5",
"054": "6",
"055": "7",
"056": "8",
"057": "9"
}
'''

charmap_filename = 'charmap-mpskit.json'

def save_default_charmap(cwd):
	charmap_path = os.path.join(cwd, charmap_filename)
	if not os.path.exists(charmap_path):
		with open(charmap_path, 'w', encoding='utf-8') as f:
			f.write(default_charmap)
		printf(charmap_path)
	else:
		printf("charmap already exists at: {}", charmap_path)

def find_charmap_path(cwd):
	""" find charmap file starting from cwd directory and searching upwards"""
		
	cur = cwd
	
	for _ in range(64):
		charmap_path = os.path.join(cur, charmap_filename)
		if os.path.exists(charmap_path):
			return charmap_path
		
		par = os.path.abspath(os.path.join(cur, os.pardir))
		if par == cur:
			return None
		cur = par
		
	warning("charmap file not found due to search depth limit; curr_dir: {}", cur)	
	return None
		
	

def load_charmap(cwd):
	charmap_path = find_charmap_path(cwd)
	if charmap_path is None:
		# warning('cannot locate charmap file: {}', charmap_filename)
		printf('using default charmap')
		# printf('you can create default charmap with: mpskit charmap create')
		# printf('it should be located in game main directory')
		
		charmap_json = default_charmap
				
	else:
		printf('charmap-path: {}', charmap_path)
		
		with open(charmap_path, encoding='utf-8') as f:
			charmap_json = f.read()

	try:
		cm = json.loads(charmap_json)	
	except json.decoder.JSONDecodeError as e:
		#import ipdb; ipdb.set_trace()
		fail("while reading charmap file: {}", str(e))

	conf.charmap_decode = {}
	conf.charmap_encode = {}
		
	for (k, v) in cm.items():
		kk = chr(int(k))
		vv = v
					
		conf.charmap_decode[kk] = vv
		conf.charmap_encode[vv] = kk
	
	printf('charmap-size: {}', len(conf.charmap_decode))
	
