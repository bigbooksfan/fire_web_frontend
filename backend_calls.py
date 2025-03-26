import socket
import time

import logging
from logger_module import get_logger

log = get_logger()

sock = None

def connect_to_socket():
	path_to_socket = '/tmp/firesocket.rt'
	global sock
	try:
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		sock.connect(path_to_socket)
		return True

	except ConnectionRefusedError as e:
		log.error('no connection to socket: ' + e)
		return False

def get_socket_answer(query1):
	#global log
	log.debug('call daemon with query: ' + query1)
	global sock
	let = len(query1) + 2
	query = str(let) + ' {' + query1 + '}'
	#print(query)
	sock.send(query.encode('utf-8'))
	time.sleep(1)

	data = sock.recv(1024*8).decode()
	if len(data) == 0:
		log.info('empty daemon response')
		return ""
	
	position_of_brace = data.find('{')
	if position_of_brace == -1:
		#get second part of message
		log.info('daemon output in 2 messages?')
		log.debug(data)
		time.sleep(0.1)
		data = sock.recv(1024*8).decode()
		
	return data[position_of_brace:]
