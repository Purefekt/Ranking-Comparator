import logging
import datetime

logger = logging
logger.basicConfig(
	filename='logs/ranking_comparator_' + str(datetime.datetime.now()) + '.log',
	filemode='w+',
	format='%(message)s',
	level=logging.INFO)
