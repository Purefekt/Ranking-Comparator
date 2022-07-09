import os
import gzip
import yaml
from fabric.api import run, env, put

from logger import logger
from const import LOCAL_PARENT_DIR, REMOTE_PARENT_DIR

with open("conf.yaml", 'r') as stream:
	yaml_loader = yaml.safe_load(stream)
	REMOTE_SERVER = yaml_loader.get('remote_server')
	USER_NAME = yaml_loader.get('user_name')
	REMOTE_PWD = yaml_loader.get('remote_pwd')


def compare(first, second, listing):
	if second is None:
		return first
	if first is None:
		return second
	elif second != first:
		listing['conflict'] = True
		return first + " , " + second
	return first


def save_raw_file(content, dir, name):
	full_dir = REMOTE_PARENT_DIR + dir
	if not os.path.isdir(full_dir):
		logger.info('Creating dir ' + full_dir)
		os.makedirs(full_dir)
	try:
		with gzip.open(full_dir + name, 'wt') as f:
			f.write(content)
			logger.info('Saved file ' + full_dir + ' ' + name)
			return full_dir + name
	# except Exception as e:
	# 	logger.error("Error while writing file locally")
	# 	logger.exception("Exception trace: ")
	# 	print("Exception while writnig file loally: " + str(e))
	# 	return None
	finally:
		f.close


def send_raw_file(content, dir, name):
	dir = dir.replace(' ', '')
	local_name = save_raw_file(content, dir, name)
	full_dir = REMOTE_PARENT_DIR + dir
	env.host_string = REMOTE_SERVER
	env.user = USER_NAME
	env.password = REMOTE_PWD
	run('mkdir -p {0}'.format(full_dir))
	put(os.path.abspath(local_name), full_dir)
	os.remove(os.path.abspath(local_name))
