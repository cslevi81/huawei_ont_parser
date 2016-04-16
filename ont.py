#!/usr/bin/python
# -*- coding: utf-8 -*-

import pycurl
import argparse
import os
import re
import hashlib
try:
	from io import BytesIO
except ImportError:
	from StringIO import StringIO as BytesIO

def dorequest(url,headers=[]):
	c = pycurl.Curl()
	buff = BytesIO()
	hdr = BytesIO()
	if args.verbose != False:
		c.setopt(pycurl.VERBOSE, True)
	if os.path.isfile('cookie.txt'):
		c.setopt(pycurl.COOKIEFILE, 'cookie.txt')
	c.setopt(pycurl.COOKIEJAR, 'cookie.txt')
	if len(headers) > 0:
		c.setopt(pycurl.HTTPHEADER, headers)
	c.setopt(pycurl.URL, url)
	try:
		c.setopt(pycurl.WRITEFUNCTION, buff.write)
		c.setopt(pycurl.HEADERFUNCTION, hdr.write)
		c.perform()
	except:
		sys.exit('Ouch, an error occured, during connection to '+url+'!')
	else:
		status_code = c.getinfo(pycurl.HTTP_CODE)
	finally:
		c.close()
	if str(status_code) == '200': #If we got good response
		out = buff.getvalue().decode('utf-8')
	else:
		sys.exit('HTTP problem: ' + str(status_code))
	return out
	
parser = argparse.ArgumentParser(description='Huawei EchoLife HG8245H GPON ONT optical informations')
parser.add_argument('-u', '--user', required=True, type=str, help='User\'s e-mail address')
parser.add_argument('-p', '--password', required=True, type=str, help='User\'s passwword')
parser.add_argument('-v','--verbose', action='store_true', help='verbose output')
args = parser.parse_args()

if os.path.isfile('cookie.txt'):
	os.remove('cookie.txt')
# 1. Login form
page_loginform = dorequest('http://192.168.1.254/')
cnt = str(re.findall('function GetRandCnt\(\) { return \'(.[^\']*)\'; }',page_loginform)[0])
if args.verbose != False:
	print (cnt)

if ((args.user != None) and (args.password != None)):
	rid = hashlib.sha256(cnt).hexdigest() + hashlib.sha256(args.user + cnt ).hexdigest() + hashlib.sha256(hashlib.sha256(hashlib.md5(args.password).hexdigest()).hexdigest() + cnt).hexdigest()
	# 2. Login page
	page_login = dorequest('http://192.168.1.254/login.cgi', ['Cookie: Cookie=rid=' + rid + ':Language:english:id=-1; path=/', 'Referer: http://192.168.1.254/'])
	if args.verbose != False:
		print (page_login)
	# 2. Index page
	page_index = dorequest('http://192.168.1.254/index.asp',['Referer: http://192.168.1.254/login.asp'])
	if args.verbose != False:
		print (page_index)
	# 3. Optical information
	page_opticinfo = dorequest('http://192.168.1.254/html/status/opticinfo.asp',['Referer: http://192.168.1.254/index.asp'])
	if args.verbose != False:
		print (page_opticinfo)
	opticinfos = re.findall('var opticInfos = new Array\(new stOpticInfo\(\"InternetGatewayDevice.X_HW_DEBUG.AMP.Optic\",\"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\"\),null\);',page_opticinfo)
	print ("TX optical power:\t" + str(opticinfos[0][0]) + ' dBm')
	print ("RX optical power:\t" + str(opticinfos[0][1]) + ' dBm')
	print ("Working voltage:\t" + str(opticinfos[0][2]) + ' mV')
	print ("Bias current:\t\t" + str(opticinfos[0][4]) + ' mA')
	print ("Working temperature:\t" + str(opticinfos[0][3]) + ' C')
else:
	sys.exit('Username and password needed!')
