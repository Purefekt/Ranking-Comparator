from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

import hashlib
import time
from urllib.parse import urlencode
from threading import Thread
from queue import Queue

from connector import get_connector
from const import EXPEDIA_RAW_HOTEL_DIR, EXPEDIA_RAW_REVIEW_DIR
from logger import logger
from utils import *

from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="geoapiExercises")


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

		# Hotel Info
		hotel_info = {}
		hotel_info['title'] = driver.find_elements(By.CSS_SELECTOR, '.uitk-spacing-padding-large-blockstart-three .uitk-heading-3')[0].text
		hotel_info['hotel_id'] = hotel[0]
		full_address = driver.find_elements(By.CSS_SELECTOR, '.uitk-text-default-theme.uitk-layout-flex-item-flex-basis-full_width')[0].text
		full_add_arr = full_address.split(',')
		hotel_info['postal_code'] = full_add_arr[len(full_add_arr)-1].strip()
		hotel_info['region'] = full_add_arr[len(full_add_arr)-2].strip()
		hotel_info['locality'] = full_add_arr[len(full_add_arr)-3].strip()
		hotel_info['street_add'] = ','.join(full_add_arr[0: len(full_add_arr)-3]).strip()
		
		hotel_info['latitude'] = driver.find_elements(By.XPATH, "//meta[@itemprop='latitude']")[0].get_attribute('content')
		hotel_info['longitude'] = driver.find_elements(By.XPATH, "//meta[@itemprop='longitude']")[0].get_attribute('content')		
		hotel_info['country'] = geolocator.reverse(hotel_info['latitude']+","+hotel_info['longitude']).raw['address'].get('country')
		print(hotel_info)
		try:
			all_reviews_button = driver.find_elements(By.CSS_SELECTOR, '.uitk-button-secondary')
			for button in all_reviews_button:
				if button.text == 'See all reviews' and button.is_enabled():
					button.click()
					save_raw_file(driver.page_source, EXPEDIA_RAW_REVIEW_DIR + '1_TRY/', hotel[0]+'.html.gz')
					time.sleep(4)
					break


			while driver.find_element(By.CSS_SELECTOR, '.uitk-spacing-margin-block-three .uitk-button-secondary'):
				more_review_buttons = driver.find_elements(By.CSS_SELECTOR, '.uitk-spacing-margin-block-three .uitk-button-secondary')
				found_element = False
				for button in more_review_buttons:
					if button.text == 'More reviews' and button.is_enabled():
						button.click()
						time.sleep(4)
						found_element = True
						break
				if not found_element:
					break
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.5);")
				time.sleep(1)
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(1)


			see_more_buttons = driver.find_elements(By.CSS_SELECTOR, '.uitk-link-medium')
			for button in see_more_buttons:
				if button.text == 'See more' and button.is_enabled():
					driver.execute_script("arguments[0].click();", button)
					time.sleep(0.2)
					time.sleep(0.2)
			time.sleep(1)

			save_raw_file(driver.page_source, EXPEDIA_RAW_REVIEW_DIR + '1_TRY/', hotel[0]+'.html.gz')
			
			reviews = driver.find_elements(By.CSS_SELECTOR, '.uitk-card-content-section-padded')
			ct = 0
			for review in reviews:
				if review.text != '':
					heading = review.find_elements(By.CSS_SELECTOR, '.uitk-heading-5 span')
					for h in heading:
						print(heading.text)
						print("--------\n")
					print("--------------------------\n")
					
			
		except Exception as e:
			logger.exception("Exception while fetching reviews")
			print("error" + str(e))
			pass
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
    print('\a')
