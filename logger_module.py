import logging
import os

logger = None

def init_logger(cwd):
	global logger
	
	if logger is not None:
		return
	
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	
	log_file = os.path.join(cwd, 'frontend.log')
	file_handler = logging.FileHandler(log_file)
	file_handler.setLevel(logging.DEBUG)
	
	file_formatter = logging.Formatter('%(levelname)s: %(message)s')
	file_handler.setFormatter(file_formatter)
	
	logger.addHandler(file_handler)
		
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	
	console_formatter = logging.Formatter('%(asctime)s, %(name)s, %(levelname)s - %(message)s')
	console_handler.setFormatter(console_formatter)
	
	logger.addHandler(console_handler)

def get_logger():
	global logger
	return logger
