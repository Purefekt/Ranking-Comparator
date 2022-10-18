from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

import hashlib
import time
from urllib.parse import urlencode
from threading import Thread
from queue import Queue

from connector import get_connector
from const import EXPEDIA_RAW_HOTEL_DIR
from logger import logger
from utils import *


class DownloadWorker(Thread):

	def __init__(self, queue):
		Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			# Get the work from the queue and expand the tuple
			try:
				param = self.queue.get()
				try:
					save_page(param)
				finally:
					self.queue.task_done()
			except:
				logger.exception("Error before processing")
				print("Error before processing")


def save_page(hotel):
	try:
		
		opts = uc.ChromeOptions()
		opts.headless = True
		opts.add_argument('--headless')
		driver = uc.Chrome(version_main=106, suppress_welcome=False, options=opts)
		url = hotel[1]
		url = 'https://www.expedia.com/Springdale-Hotels-Harvest-House-Bed-Breakfast.h56972841.Hotel-Information'
		if '?' in url:
			url = url[:url.index('?')]
		logger.info("URl: " + url)
		print(url)
		driver.get(url)
		time.sleep(10)
		driver.set_window_size(width=1200, height=831)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
		time.sleep(1)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)

		save_raw_file(driver.page_source, EXPEDIA_RAW_HOTEL_DIR + '1_TRY/', hotel[0]+'.html.gz')
		# send_raw_file(driver.page_source, EXPEDIA_RAW_DIR + 'RUNDATE_' + str(today) + '/' + loc[0].replace(' (and vicinity)', '') + '/' + str(start_date) + '__' + str(end_date) + '/', 'page.html.gz')

		# try:
		# 	all_reviews_button = driver.find_elements(By.CSS_SELECTOR, '.uitk-spacing-margin-block-three .uitk-button-secondary')
		# 	for button in all_reviews_button:
		# 		if button.text == 'See all reviews' and button.is_enabled():
		# 			button.click()
		# 			time.sleep(4)
		# 			break

		# 	while driver.find_element(By.CSS_SELECTOR, '.uitk-spacing-margin-block-three .uitk-button-secondary'):
		# 		more_review_buttons = driver.find_elements(By.CSS_SELECTOR, '.uitk-spacing-margin-block-three .uitk-button-secondary')
		# 		found_element = False
		# 		for button in more_review_buttons:
		# 			if button.text == 'More reviews' and button.is_enabled():
		# 				button.click()
		# 				time.sleep(4)
		# 				found_element = True
		# 				break
		# 		if not found_element:
		# 			break
		# 		driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.5);")
		# 		time.sleep(1)
		# 		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		# 		time.sleep(1)
		# 	print("saving")
		# 	save_raw_file(driver.page_source, EXPEDIA_RAW_HOTEL_DIR + '1_TRY/', hotel[0]+'.html.gz')
		# except Exception as e:
		# 	print("error" + str(e))
		# 	pass
	except Exception as e:
		logger.error("Expedia Error before listing")
		logger.exception("Exception: ")
		print(e)
		print('\a')
		print('\a')
		print('\a')
		print('\a')
		print('\a')
	finally:
		driver.close()


def fetch_hotel_pages():
	try:
		queue = Queue()
		# Create worker threads
		for x in range(1):
			worker = DownloadWorker(queue)
			# Setting daemon to True will let the main thread exit even though the workers are blocking
			worker.daemon = True
			worker.start()
		try:
			con = get_connector()
			hotels = con.get_expedia_hotel_urls()
		except Exception as e:
			print("Initialization failed")
			print(e)
			return
		finally:
			con.close()
		for h in hotels:
			queue.put(h)
		queue.join()
	except:
		logger.exception("Error while running parallel threads")
		print("Error while running parallel threads")


if __name__ == '__main__':
    fetch_hotel_pages()
