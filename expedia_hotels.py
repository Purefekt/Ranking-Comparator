import traceback
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
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
				traceback.print_exc()
				logger.exception("Error before processing")
				print("Error before processing")


def save_page(hotel):
	try:
		opts = uc.ChromeOptions()
		opts.headless = True
		opts.add_argument('--headless')
		driver = uc.Chrome(version_main=106, suppress_welcome=False, options=opts)

		# options = Options()
		# options.headless = True
		# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
		
		url = hotel[1]
		print(hotel[0])
		if '?' in url:
			url = url[:url.index('?')]
		logger.info("URl: " + url)
		driver.get(url)
		
		time.sleep(6)
		driver.set_window_size(width=1200, height=831)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
		time.sleep(0.5)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(0.5)

		save_raw_file(driver.page_source, EXPEDIA_RAW_HOTEL_DIR + '1_TRY/', hotel[0] + '.html.gz')
		# send_raw_file(driver.page_source, EXPEDIA_RAW_DIR + 'RUNDATE_' + str(today) + '/' + loc[0].replace(' (and vicinity)', '') + '/' + str(start_date) + '__' + str(end_date) + '/', 'page.html.gz')
		
		# Hotel Info
		hotel_info = {}
		hotel_info['title'] = driver.find_elements(By.CSS_SELECTOR, '.uitk-heading-3')[0].text
		hotel_info['hotel_id'] = hotel[0]
		full_address = driver.find_elements(By.CSS_SELECTOR, '.uitk-text-default-theme.uitk-layout-flex-item-flex-basis-full_width')[0].text
		full_add_arr = full_address.split(',')
		hotel_info['postal_code'] = full_add_arr[len(full_add_arr) - 1].strip()
		hotel_info['region'] = full_add_arr[len(full_add_arr) - 2].strip()
		hotel_info['locality'] = full_add_arr[len(full_add_arr) - 3].strip()
		hotel_info['street_add'] = ','.join(full_add_arr[0: len(full_add_arr) - 3]).strip()

		hotel_info['latitude'] = float(driver.find_elements(By.XPATH, "//meta[@itemprop='latitude']")[0].get_attribute('content'))
		hotel_info['longitude'] = float(driver.find_elements(By.XPATH, "//meta[@itemprop='longitude']")[0].get_attribute('content'))
		hotel_info['country'] = geolocator.reverse(str(hotel_info['latitude']) + "," + str(hotel_info['longitude'])).raw['address'].get('country')

		r_ids = set()
		try:
			con = get_connector()
			con.enter_expedia_hotel_info(hotel_info)
			con.close()
		except Exception as e:
			if "for key 'PRIMARY'" in str(e):
				r_ids = con.get_expedia_hotel_review_ids(hotel_info['hotel_id'])
				print("gotchaaaaaaaa Completed: " + str(len(r_ids)))
				# print(r_ids)
				con.close()
			else:
				traceback.print_exc()
				print("SQL connection failed")
				print(e)
				logger.exception("SQL connection failed: ")
				return
		

		review_box = [a.text for a in driver.find_elements(By.CSS_SELECTOR, '.uitk-empty-state-body, .uitk-spacing-margin-blockstart-six')]
		if 'No reviews yet' in review_box or 'Be the first to leave a review for this property after your stay.' in review_box:
			try:
				con = get_connector()
				con.mark_hotel_compplete(hotel[0])
				print("Completed")
				con.close()
			except Exception as e:
				traceback.print_exc()
				print("SQL connection failed")
				print(e)
				logger.exception("SQL connection failed: ")
			finally:
				return

		all_reviews_button = driver.find_elements(By.CSS_SELECTOR, '.uitk-button-secondary')
		for button in all_reviews_button:
			if button.text == 'See all reviews' and button.is_enabled():
				button.click()
				save_raw_file(driver.page_source, EXPEDIA_RAW_REVIEW_DIR + '1_TRY/', hotel[0] + '.html.gz')
				time.sleep(2)
				break
		while driver.find_element(By.CSS_SELECTOR, '.uitk-spacing-margin-block-three .uitk-button-secondary'):
			more_review_buttons = driver.find_elements(By.CSS_SELECTOR, '.uitk-spacing-margin-block-three .uitk-button-secondary')
			found_element = False
			for button in more_review_buttons:
				print('Pressing more')
				if button.text == 'More reviews' and button.is_enabled():
					button.click()
					time.sleep(3)
					found_element = True
					break
			if not found_element:
				break
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.5);")
			time.sleep(0.5)
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(0.5)

		see_more_buttons = driver.find_elements(By.CSS_SELECTOR, '.uitk-link-medium')
		for button in see_more_buttons:
			if button.text == 'See more' and button.is_enabled():
				driver.execute_script("arguments[0].click();", button)
				time.sleep(0.2)
				time.sleep(0.2)
		time.sleep(1)
		save_raw_file(driver.page_source, EXPEDIA_RAW_REVIEW_DIR + '1_TRY/', hotel[0] + '.html.gz')

		reviews = driver.find_elements(By.CSS_SELECTOR, 'section .uitk-card .uitk-card-content-section-padded')
		
		ct = 0
		

		for review in reviews:
			
			if review.text != '':
				heading = review.find_elements(By.CSS_SELECTOR, '.uitk-heading-5 span')
				if len(heading) == 1 and heading[0].text != '':
					review_info = {
						'title': None,
						'disliked': None,
						'liked': None,
						'owner_response': None,
						'owner_response_date': None,
						'owner': None,
						'review_text': None,
						'photos': '',
						'photos_count': 0
					}

					review_info['review_id'] = review.find_elements(By.XPATH, ".//article[@itemprop='review']")[0].get_attribute('id')
					if review_info['review_id'] in r_ids:
						continue
					r_ids.add(review_info['review_id'])
					
					print("wwwwhere")
					review_info['rating'] = heading[0].text
					review_info['user'] = review.find_elements(By.CSS_SELECTOR, '.uitk-heading-7')[0].text
					for a in review.find_elements(By.CSS_SELECTOR, '.uitk-spacing-margin-blockstart-two'):
						if a.text.startswith('Liked'):
							review_info['liked'] = a.text[6:]
						if a.text.startswith('Disliked'):
							review_info['disliked'] = a.text[10:]
					for a in review.find_elements(By.CSS_SELECTOR, '.uitk-spacing-padding-blockend-two+ section .uitk-text-default-theme'):
						try:
							review_info['date'] = datetime.strptime(a.text, '%b %d, %Y').date()
							break
						except Exception as e:
							logger.exception("Exp: ")
					title = review.find_elements(By.CSS_SELECTOR, '.uitk-heading-6 span')
					if len(title) > 0:
						review_info['title'] = title[0].text
					review_text = review.find_elements(By.CSS_SELECTOR, '.display-lines span')
					if len(review_text) > 0:
						review_info['review_text'] = review_text[0].text
					if review.find_elements(By.CSS_SELECTOR, '.uitk-spacing-margin-blockstart-three')[0].text == '':
						continue
					else:
						review_info['like_count'] = int(review.find_elements(By.CSS_SELECTOR, '.uitk-spacing-margin-blockstart-three')[0].text)
					
					photos = review.find_elements(By.CSS_SELECTOR, '.uitk-layout-grid-display-grid.uitk-spacing-padding-block-two figure div img')
					for photo in photos:
						review_info['photos'] += (photo.get_attribute('src') + ' , ')
					review_info['photos_count'] = len(photos)
					resp = review.find_elements(By.CSS_SELECTOR, '.uitk-spacing-border-inlinestart')
					if len(resp) > 0:
						review_info['owner_response'] = resp[0].find_elements(By.CSS_SELECTOR, '.uitk-spacing-padding-block-two')[0].text
						meta = resp[0].find_elements(By.CSS_SELECTOR, '.uitk-type-bold')[0].text
						review_info['owner_response_date'] = datetime.strptime(meta[-12:].strip() , '%b %d, %Y').date()
						review_info['owner'] = meta[14:-15]
					review_info['hotel_id'] = hotel[0]
					try:
						con = get_connector()
						con.enter_expedia_review_info(review_info)
						con.close()
					except Exception as e:
						if "for key 'PRIMARY'" in str(e):
							print("Duplicate entry: ")
							# print(r_ids)
							con.close()
						else:
							traceback.print_exc()
							print("SQL connection failed")
							print(e)
							logger.exception("SQL connection failed: ")
							return
			print("next")
		try:
			con = get_connector()
			con.mark_hotel_compplete(hotel[0])
			print("Completed")
			con.close()
		except Exception as e:
			traceback.print_exc()
			print("SQL connection failed")
			print(e)
			logger.exception("SQL connection failed: ")
			return
	except Exception as e:
		# logger.error("Expedia Error before listing")
		# logger.exception("Exception: ")
		traceback.print_exc()
		print(e)
		print('\a')
		print('\a')
		print('\a')
		print('\a')
		print('\a')
	finally:
		driver.close()


def fetch_hotel_pages():
	logger.info("where are you")
	try:
		queue = Queue()
		# Create worker threads
		for x in range(50):
			worker = DownloadWorker(queue)
			# Setting daemon to True will let the main thread exit even though the workers are blocking
			worker.daemon = True
			worker.start()
		try:
			con = get_connector()
			hotels = con.get_expedia_hotel_urls()
			print("Length: " + str(len(hotels)))
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
