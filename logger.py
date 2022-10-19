import logging
import datetime

logger = logging
logger.basicConfig(
	filename='logs/ranking_comparator_' + str(datetime.datetime.now()) + '.log',
	filemode='w',
	format='%(funcName)s(%(lineno)s) - %(message)s',
	level=logging.INFO)
