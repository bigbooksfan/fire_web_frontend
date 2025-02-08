import socket
import json
import xml.etree.ElementTree as ET
import time
import webbrowser
import pyautogui
import os
import xmltodict
from flask import Flask, render_template, redirect
from multiprocessing import Process

def add_table_zone(name):
	return "<tr style=\"height:80px\"><td style=\"width:310px\">{}</td></tr>".format(name)
	
def add_train(board_id, loop_id):
	return "<tr style=\"height:80px\"><td style=\"width:310px\">board {} / loop {}</td></tr>".format(board_id, loop_id)

def show_zones():
	print('enter zones renderer')
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
	print('enter main renderer')
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
	att = ": "
	for attrib in element.attrib:
		att += attrib + ": " + str(element.attrib[attrib]) + ", "
		print("  " * lvl + element.tag + " " + att)

	if element.text:
		text = element.text.strip()
		if text:
			print("  " * lvl + text)
			
	for child in element:
		print_xml_tree(child, lvl + 1)

path_to_socket = '/tmp/firesocket.rt'

try:
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.connect(path_to_socket)

except ConnectionRefusedError as e:
	print('no connection to socket: ', e)
	quit()

def get_socket_answer(query1):
	let = len(query1) + 2
	query = str(let) + ' {' + query1 + '}'
	#print(query)
	sock.send(query.encode('utf-8'))
	time.sleep(1)

	data = sock.recv(1024*8).decode()
	if len(data) == 0:
		print('empty daemon response')
		return ""
	
	position_of_brace = data.find('{')
	if position_of_brace == -1:
		#get second part of message
		print('daemon output in 2 messages?')
		print(data)
		quit()
		pass
	
	return data[position_of_brace:]

config_data = get_socket_answer('"args":null,"cmd":"getconfig"')

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
print_xml_tree(root)

config_json = xmltodict.parse(config_json_data['resp']['cfgxml'])
#print(config_json)
#aaas = json.dumps(config_json, indent=4, ensure_ascii=False)
#print(aaas)
for n in range(4):
	for p in config_json['fire']['station']['zones'][n]['zone']:
		print(p)
#exit()

# add item to watchlist
'''
arg = "/board_0/port_0/loop_0/sensor_001/in/status"
raw_text = "\"args\":[\"" + arg + "\"],\"cmd\":\"addreadparamstopool\""
print(raw_text)

data = get_socket_answer(raw_text)
print(data)

raw_text = "\"args\":null,\"cmd\":\"getreadparamfrompool\""
print("getting params:")
print(raw_text)

pools_data = get_socket_answer(raw_text)
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
	
signaling_table=""
for zone in signalization:
	signaling_table += add_table_zone(zone['@name'])

notification_table=""
for zone in notification:
	notification_table += add_table_zone(zone['@name'])

firefighting_table=""
for zone in firefighting:
	firefighting_table += add_table_zone(zone['@name'])

smoke_removal_table=""
for zone in smoke_removal:
	smoke_removal_table += add_table_zone(zone['@name'])

#build trains	
trains_table=""

boards_json = config_json['fire']['station']['board']
txt_data = json.dumps(boards_json, indent=4)
print(txt_data)

board_id = boards_json['@id']
for port in boards_json['port']:
	if port['@type'] == 'unused':
		continue
	#print(port)
	loop_id = port['loop']['@id']
	print('board {} / loop {}'.format(board_id, loop_id))
	trains_table += add_train(board_id, loop_id)
	#pass

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

@app.route('/journal')
def route():
	return render_template("journal.html")

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


#browser = webbrowser.get()
#cwd = os.path.dirname(os.path.abspath(__file__))
#browser.open('localhost:5000')

#time.sleep(15)
#pyautogui.press('f11')

print("Enter periodic")
while True:
	time.sleep(5)
	print('tick')
	
	#data = get_socket_answer('\"args\":null,\"cmd\":\"getreadparamfrompool\"')
	#print(data)
	
	#json_data = json.loads(data)
	#if len(json_data['resp']['params']) > 0:
		#candidate = json_data['resp']['params'][0]['i']
		#if value_to_check != candidate:
			#print("REWRITE!")
			#value_to_check = candidate
	
	#data = get_socket_answer('\"args\":null,\"cmd\":\"getjournal\"')
	#print(data)
	#pyautogui.press('f5')

socket.close()
