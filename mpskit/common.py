""" Copyright 2015-2017  sta256+mpskit at gmail.com
    
    This file is part of mpskit.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY.

    See LICENSE file for more details.
"""

from typing import IO
from io import BytesIO
import json
import struct, os, os.path, sys, io
import _io, sys
from mpskit.conf import conf
from mpskit.record import Record
from mpskit.fail import fail
from PIL import Image

class Error(Exception): 
	def __str__(self):
		return format(*self.args)
	



def save_image(name: str, img, **param):
	oname = name+'.png'	
	img.save(oname, **param)
	print(oname)
	



def save_header(name: str, h):
	oname = name + '.json'
	with open(oname, 'w') as f:
		json.dump(h.as_dict(), f, indent=2)	
	print(oname)


g_curr_dir = ''

def open2(name: str, flags) -> IO:
	if isinstance(name,_io._IOBase):		
		return name
	else:
		return open(name, flags)

def output(fname: str) -> None:
	print(os.path.join(g_curr_dir, fname))
	


def read_idstring(f: IO, idstring):
	x = f.read(len(idstring))
	if x != idstring:
		raise Error("invalid idstring: {}; expected={};  ".format(repr(x), repr(idstring)))

def check_magic(x, y):
	if x != y:
		raise Error("invalid magic: {} != {};  ".format(repr(x), repr(y)))

verbose = 1

	
def read_struct(f: IO, fmt):
	data = f.read(struct.calcsize(fmt))
	return struct.unpack(fmt, data)
	
def calcsize(fmt: str) -> int:
	return struct.calcsize(fmt)
	
reads = read_struct

def read(f: IO, fmt):
	return read_struct(f,fmt)[0]


def read_until(f: IO, b=0) -> bytes:	
	xs = []
	while 1:
		x = read_uint8(f)
		xs.append(x)
		#import ipdb; ipdb.set_trace()
		if x == b:
			break
			
	return bytes(xs)
	
	
def get_asciiz(buf):	
	i = buf.find(b'\x00')
	return buf[:i].decode('ascii')

def write_struct(f: IO, fmt, ts) -> int:	
	return f.write(struct.pack(fmt, *ts))
	#return struct.calcsize(fmt)
	

def read_raw(f: IO, n: int):
	return [x for x in f.read(n)]
	#return read_struct(f, '<B')[0]



def write_raw(f: IO, n: int, bs) -> int:
	assert len(bs) == n
	i = 0
	for b in bs:
		assert 0 <= b < 256
		write_uint8(f, b)
		i += 1
	return i

def check_ext(name: str, ext: str) -> None:
	if not name.upper().endswith(ext.upper()):
		fail('invalid extension: expected={}; file={};', ext, name)

def read_raw(f: IO, n):
	return f.read(n)
	#return [x for x in f.read(n)]
	#return read_struct(f, '<B')[0]



def decode_buffer(xs):
	return xs.decode('latin1')
	
		
def encode_buffer(xs):
	return xs.encode('latin1')
		

	
def read_uint8(f: IO) -> int:
	return read_struct(f, '<B')[0]
		
def read_uint16(f: IO) -> int:
	return read_struct(f, '<H')[0]


def read_int16(f: IO) -> int:
	return read_struct(f, '<h')[0]

def read_sint16(f: IO) -> int:
	return read_struct(f, '<h')[0]


def read_uint32(f: IO) -> int:
	return read_struct(f, '<I')[0]
	
def read_int32(f: IO) -> int:
	return read_struct(f, '<i')[0]

	
def write_uint8(f: IO, val: int):
	write_struct(f, '<B', (val,))
	return 1
	
def write_uint16(f: IO, val: int):
	return write_struct(f, '<H', (val,))

def write_sint16(f: IO, val: int):
	return write_struct(f, '<h', (val,))

def write_int16(f: IO, val: int):
	return write_struct(f, '<h', (val,))
	
def write_uint32(f: IO, val: int):
	return write_struct(f, '<I', (val,))
		
def write_int32(f: IO, val: int):
	return write_struct(f, '<i', (val,))
	



def write_ascii(f: IO, s):
	for b in s.encode('ascii'):
		write_uint8(f, b)


def warning(fmt, *args):
	print('WARNING: ' + fmt.format(*args))
	

def write_string(f: IO, n, s):
	if len(s) > n:
		fail('string too long (must be < {}): {}', n, s)
				
	for ch in s:
		byte = ord(ch)
		assert 0 <= byte <= 255
		write_uint8(f, byte)
			
	return n


META_SQUARE_BRACKETS = True   # charmap wont be applied to [] and anything inside them

def decode_string(b, null_term=False):
	"""
	null_term -- strip null and anything past it
	"""
	assert isinstance(b, (bytes, list))
	
	xs = []
	for byte in b:		
		if null_term and byte == 0:
			break
		assert (0 <= byte < 128)
		#import ipdb; ipdb.set_trace()
		xs.append(chr(byte))
		
	# replace
	charmap_enabled = True
	for i in range(len(xs)):
		x = xs[i]
		
		# don't map anything inside []
		if x == '[' and META_SQUARE_BRACKETS:			
			charmap_enabled = False
			
		if charmap_enabled:
			y = conf.charmap_decode.get(x, None)
			if y != None:
				xs[i] = y
		
		if x == ']' and META_SQUARE_BRACKETS:
			charmap_enabled = True
				
		
		
	return ''.join(xs)
		
def encode_string(s, null_term=False, max_len=None, fill=False):
	"""
	null_term -- add null at the end of string if not already present
	max_len -- raise error when string is longer then max_len after encoding
	fill -- fill to max_len with nulls
	"""	
	
	xs = list(s)
	
	# replace
	charmap_enabled = True	
	for i in range(len(xs)):
		x = xs[i]
		
		# don't map anything inside []		
		if x == '[' and META_SQUARE_BRACKETS:			
			charmap_enabled = False
		
		if charmap_enabled:
			y = conf.charmap_encode.get(xs[i], None)
			if y != None:
				xs[i] = y
				
		if x == ']' and META_SQUARE_BRACKETS:
			charmap_enabled = True
		
	if null_term and xs[-1:] != ["\x00"]:
		xs.append("\x00")
	
	b = ''.join(xs).encode('ascii')
	
	if max_len is not None and len(b) > max_len:
		fail('this string must be shorter then {} chars: {}', max_len, s)
	
	if fill:
		b = b + b''.join([b'\x00'] * (max_len - len(b)))
	return b



Header = Record
