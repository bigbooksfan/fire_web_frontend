#import socket
import json
import xml.etree.ElementTree as ET
import time
import webbrowser
import pyautogui
import os
import xmltodict
from flask import Flask, render_template, redirect, request
from multiprocessing import Process

import logger_module

cwd = os.path.dirname(os.path.abspath(__file__))
try:
	os.remove(os.path.join(cwd, 'frontend.log'))		# New log-file in every start. REMOVE IT LATER!!!!
except FileNotFoundError:
	pass
logger_module.init_logger(cwd)
log = logger_module.get_logger()

log.debug('TEST debug message')
log.info('TEST info message')
log.warning('TEST warning message')
log.error('TEST error message')
log.critical('TEST critical message')

log.info('frontend script start')

import html_parts
import backend_calls

def show_zones():
	#print('enter zones renderer')
	log.debug('enter zones renderer')
	with open("index.html", "w") as page, open("html_templates/open.html", "r") as first, open("html_templates/close.html", "r") as last, open("html_templates/zones.html", "r") as zones:
		buf = first.read()
		page.write(buf)
		buf = zones.read()
		page.write(buf)
		buf = last.read()
		page.write(buf)
	page.close()
	first.close()
	last.close()
	zones.close()	
	
	time.sleep(1)
	pyautogui.press('f5')

def show_main():
	#print('enter main renderer')
	log.debug('enter main renderer')
	with open("index.html", "w") as page, open("html_templates/open.html", "r") as first, open("html_templates/close.html", "r") as last, open("html_templates/main.html", "r") as main:
		buf = first.read()
		page.write(buf)
		buf = main.read()
		page.write(buf)
		buf = last.read()
		page.write(buf)
	page.close()
	first.close()
	last.close()
	
	time.sleep(1)
	pyautogui.press('f5')

def print_xml_tree(element, lvl = 0):
	ret = ""
	att = ": "
	for attrib in element.attrib:
		att += attrib + ": " + str(element.attrib[attrib]) + ", "
		#print("  " * lvl + element.tag + " " + att)
		ret += str("  " * lvl + element.tag + " " + att) + '\n'

	if element.text:
		text = element.text.strip()
		if text:
			#print("  " * lvl + text)
			ret += str("  " * lvl + text) + '\n'
			
	for child in element:
		print_xml_tree(child, lvl + 1)
	
	return ret

if backend_calls.connect_to_socket() is False:
	#Error
	pass

config_data = backend_calls.get_socket_answer('"args":null,"cmd":"getconfig"')
config_json_data = json.loads(config_data)
#print(config_json_data)

#print('parse resp cfgxml')
#xml_data = ET.fromstring(config_json_data['resp']['cfgxml'])
#print(xml_data)
#for station in xml_data.iter('config'):
    #print(station.text)

tree = ET.ElementTree(ET.fromstring(config_json_data['resp']['cfgxml']))
#print('try to build a tree')
root = tree.getroot()
tree_text = print_xml_tree(root)
log.info(tree_text)

log.debug('zones structure')
config_json = xmltodict.parse(config_json_data['resp']['cfgxml'])
for n in range(4):
	for p in config_json['fire']['station']['zones'][n]['zone']:
		#print(p)
		log.debug(str(p))	
#exit()

# add item to watchlist
'''
arg = "/board_0/port_0/loop_0/sensor_001/in/status"
raw_text = "\"args\":[\"" + arg + "\"],\"cmd\":\"addreadparamstopool\""
print(raw_text)

data = backend_calls.get_socket_answer(raw_text)
print(data)

raw_text = "\"args\":null,\"cmd\":\"getreadparamfrompool\""
print("getting params:")
print(raw_text)

pools_data = backend_calls.get_socket_answer(raw_text)
print(pools_data)

print("parsed")
json_data = json.loads(pools_data)
print(json_data)

value_to_check = json_data['resp']['params'][0]['i']
print("value to check: " + str(value_to_check))
'''

#collect zones
signalization = []
notification = []
firefighting = []
smoke_removal = []

for zone in config_json['fire']['station']['zones'][0]['zone']:
	signalization.append(zone)
for zone in config_json['fire']['station']['zones'][1]['zone']:
	notification.append(zone)
for zone in config_json['fire']['station']['zones'][2]['zone']:
	firefighting.append(zone)
for zone in config_json['fire']['station']['zones'][3]['zone']:
	smoke_removal.append(zone)
	
print(signalization)
signaling_table=""
for zone in signalization:
	signaling_table += html_parts.add_table_zone(zone['@name'])

notification_table=""
for zone in notification:
	notification_table += html_parts.add_table_zone(zone['@name'])

firefighting_table=""
for zone in firefighting:
	firefighting_table += html_parts.add_table_zone(zone['@name'])

smoke_removal_table=""
for zone in smoke_removal:
	smoke_removal_table += html_parts.add_table_zone(zone['@name'])

#build trains	
trains_table=""

boards_json = config_json['fire']['station']['board']
txt_data = json.dumps(boards_json, indent=4)
#print(txt_data)
log.debug('boards data:')
log.debug(txt_data)

board_id = boards_json['@id']
for port in boards_json['port']:
	if port['@type'] == 'unused':
		continue
	#print(port)
	loop_id = port['loop']['@id']
	print('board {} / loop {}'.format(board_id, loop_id))
	trains_table += html_parts.add_train(board_id, loop_id)
	#pass

journal_list = ""

s = "not okei"
#render webpages, start Flask
app = Flask(__name__)

@app.route('/main')
@app.route('/')
def home():
	return render_template("main.html")

@app.route('/zones')
def zones():
	return render_template("zones.html", content=s, 
		signaling_table=signaling_table,
		notification_table=notification_table,
		firefighting_table=firefighting_table,
		smoke_removal_table=smoke_removal_table)

tmp_page = '''<!DOCTYPE html>
<html>
  <head>
  </head>
  <body>  
	  qwerty
	  <object data="data.txt"></object>
  </body>
</html>
'''

@app.route('/journal', methods=["GET", "POST"])
def route():
	if request.method == "GET":		
		#open file here
		path_to_file = os.path.join(cwd, "dynamic_data/journal.txt")
		with open(path_to_file, "r") as f:
			journal_list = f.read()
			f.close()
		#journal_list = journal_list_tmp
	return render_template("journal.html", journal_list=journal_list)
	#return tmp_page

@app.route('/trains')
def trains():
	return render_template("trains.html",
		trains_table=trains_table)

@app.route('/statuses')
def statuses():
	return render_template("statuses.html")
	
def run_app():
	app.run()
	
process = Process(target=run_app)
process.start()

os.system("firefox --kiosk localhost:5000 &")
#browser = webbrowser.get()
#browser.open('localhost:5000')

#time.sleep(15)
#pyautogui.press('f11')

path_to_file = os.path.join(cwd, "dynamic_data/journal.txt")
with open(path_to_file, "w") as f:
	f.truncate()

print("Enter periodic")
while True:
	time.sleep(5)
	print('tick')
	
	with open("front/dynamic_data/journal.txt", "a") as f:
		f.write(html_parts.add_journal_row())
		f.close()
	
	#data = backend_calls.get_socket_answer('\"args\":null,\"cmd\":\"getreadparamfrompool\"')
	#print(data)
	
	#json_data = json.loads(data)
	#if len(json_data['resp']['params']) > 0:
		#candidate = json_data['resp']['params'][0]['i']
		#if value_to_check != candidate:
			#print("REWRITE!")
			#value_to_check = candidate
	
	#data = backend_calls.get_socket_answer('\"args\":null,\"cmd\":\"getjournal\"')
	#print(data)
	#pyautogui.press('f5')

socket.close()
