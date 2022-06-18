import os
import gzip

from logger import logger

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
	if not os.path.isdir(dir):
		logger.info('Creating dir ' + dir)
		os.makedirs(dir)
	try:
		with gzip.open(dir + name, 'wt') as f:
			f.write(content)
			logger.info('Saved file ' + dir + ' ' + name)
	finally:
		f.close
