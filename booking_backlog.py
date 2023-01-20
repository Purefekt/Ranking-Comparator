import os
import traceback
import hashlib
from connector import get_connector
from const import BOOKING_RAW_DIR, REMOTE_PARENT_DIR, CHROME_VERSION
from logger import logger
from utils import *
import sys
import time
from threading import Thread
from queue import Queue
from urllib.parse import urlencode
import datetime
import gzip
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
import glob

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


def save_page(info):	
	try:
		today = info[1]
		start_date = info[2]
		end_date = info[3]
		loc = info[0]
		try:
			con = get_connector()
			# con.shift_booking_rankings(loc, today, start_date)
			con.clean_booking_rankings(loc, today, start_date)
		except Exception as e:
			print("Initialization failed: " + str(e))
			return
		finally:
			con.close()
		dirr = REMOTE_PARENT_DIR + BOOKING_RAW_DIR + 'RUNDATE_' + str(today) + '/' + loc + '/' + str(start_date) + '__' + str(end_date) 
		# response = remote_command('ls {0}'.format(dirr.replace(' ', '\ '))).replace('page', '').replace('.html.gz', '').split(' ')
		# response = list(filter(lambda x: len(x)>0, response))
		get_file(dirr + '/*')
		# pages = len(response)
		pages = len(glob.glob1('./test/',"*.html.gz"))
		print(pages)
		page = 1
		i = 1
		while page <= pages:
			print(page)
			with gzip.open('./test/page'+str(page)+'.html.gz', 'rb') as f_in:
			    with open('./test/page'+str(page)+'.html', 'wb') as f_out:
			        shutil.copyfileobj(f_in, f_out)
			
			driver = webdriver.Chrome(executable_path='./chromedriver')
			p = driver.get('file:/Users/dproserp/RA_Projects/Ranking-Comparator/test/page'+str(page)+'.html')
			
			time.sleep(5)
			listings = driver.find_elements(By.XPATH, "//div[@data-testid='property-card']")
	
			for li in listings:
				try:
					listing = {
						'hotel_id': None,
						'cover_image': None,
						'url': None,
						'name': None,
						'locality': None,
						'map_url': None,
						'distance_from_center': None,
						'location_addon': None,
						'rating': None,
						'review_count': None,
						'comment': None,
						'external_rating': None,
						'external_comment': None,
						'external_review_count': None,
						'recommended_unit': None,
						'recommended_unit_beds': None,
						'availability': None,
						'occupancy': None,
						'original_price': '',
						'discounted_price': '',
						'badges': [],
						'sponsored': False
					}
					info_array = li.text.splitlines()

					# Removing excess info
					info_array = list(filter(lambda a: a != "Opens in new window", info_array))
					info_array = list(filter(lambda a: a != "See availability", info_array))

					for a in info_array:
						if a == 'Ad':
							listing['sponsored'] = True
							info_array.remove(a)
							break

					cover_image = li.find_elements(By.CSS_SELECTOR, "div > div > div > div > a > img")
					listing['cover_image'] = [photo.get_attribute("src") for photo in cover_image][0]

					url = li.find_elements(By.CSS_SELECTOR, "div > div > div > div > a")
					listing['url'] = [photo.get_attribute("href") for photo in url][0]

					name = li.find_elements(By.CSS_SELECTOR, "h3 > a > div")
					listing['name'] = [photo.text for photo in name][0]
					info_array = list(filter(lambda a: a != listing['name'], info_array))

					# logger.info("Name: " + listing['name'])
					listing['locality'] = li.find_elements(By.CSS_SELECTOR, "span[data-testid='address']")[0].text
					location = li.find_elements(By.CSS_SELECTOR, "div[data-testid='location']")[0]
					listing['map_url'] = location.find_elements(By.CSS_SELECTOR, "div > a")[0].get_attribute("href")
					if ' miles from center' in location.text:
						listing['location_addon'] = location.text[location.text.index(' miles from center') + 18:]
						listing['distance_from_center'] = li.find_elements(By.CSS_SELECTOR, "span[data-testid='distance']")[0].text[:-18]
					elif ' feet from center' in location.text:
						listing['location_addon'] = location.text[location.text.index(' feet from center') + 17:]
						listing['distance_from_center'] = li.find_elements(By.CSS_SELECTOR, "span[data-testid='distance']")[0].text[:-17]
					info_array = list(filter(lambda a: a != location.text, info_array))

					if 'New to Booking.com' not in info_array:
						rating_arr = li.find_elements(By.CSS_SELECTOR, "div[data-testid='review-score']")
						if len(rating_arr) > 0:
							rating = rating_arr[0]
							listing['rating'] = rating.find_elements(By.CSS_SELECTOR, "div > div:nth-child(1)")[0].text
							listing['comment'] = rating.find_elements(By.CSS_SELECTOR, "div > div:nth-child(2) > div:nth-child(1)")[0].text
							listing['review_count'] = rating.find_elements(By.CSS_SELECTOR, "div > div:nth-child(2) > div:nth-child(2)")[0].text
							info_array = list(filter(lambda a: a != listing['rating'] and a != listing['comment'] and a != listing['review_count'], info_array))
							if 'reviews' in listing['review_count']:
								listing['review_count'] = listing['review_count'][:-8].replace(',', '')
							else:
								listing['review_count'] = listing['review_count'][:-7].replace(',', '')
							if listing['review_count'] == '':
								listing['review_count'] = None
						rating_arr = li.find_elements(By.CSS_SELECTOR, "div[data-testid='external-review-score']")
						if len(rating_arr) > 0:
							rating = rating_arr[0]
							ext = rating.find_elements(By.CSS_SELECTOR, "div > div > div:nth-child(1)")[0].text
							listing['external_rating'] = ext[ext.index(' ') + 1:]
							listing['external_comment'] = ext[:ext.index(' ')]
							listing['external_review_count'] = rating.find_elements(By.CSS_SELECTOR, "div > div > div:nth-child(2)")[0].text
							info_array = list(filter(lambda a: a != listing['external_rating'] + ' ' + listing['external_comment'] and a != listing['external_review_count'], info_array))
							if 'reviews' in listing['external_review_count']:
								listing['external_review_count'] = listing['external_review_count'][:-17].replace(',', '')
							else:
								listing['external_review_count'] = listing['external_review_count'][:-16].replace(',', '')

					rec_unit = li.find_elements(By.CSS_SELECTOR, "div[data-testid='recommended-units']")[0]
					try:
						listing['recommended-unit'] = rec_unit.find_elements(By.CSS_SELECTOR, " div > div > div > div:nth-child(1) > span")[0].text
						listing['recommended-unit-beds'] = rec_unit.find_elements(By.CSS_SELECTOR, " div > div > div > div:nth-child(2)")[0].text
						availability = rec_unit.find_elements(By.CSS_SELECTOR, " div > div > div > div:nth-child(3)")
						if len(availability) > 0:
							listing['availability'] = availability[0].text
						info_array = list(filter(lambda a: a != listing['recommended-unit'] and a != listing['recommended-unit-beds'] and a != listing['availability'], info_array))
					except:
						pass

					occupancy = li.find_elements(By.CSS_SELECTOR, "div[data-testid='price-for-x-nights']")
					if len(occupancy) > 0:
						listing['occupancy'] = occupancy[0].text
					price = li.find_elements(By.CSS_SELECTOR, "div[data-testid='price-and-discounted-price'] > span:nth-child(1)")
					price2 = li.find_elements(By.CSS_SELECTOR, "div[data-testid='price-and-discounted-price'] > span:nth-child(2)")
					try:
						if len(price2) > 0:
							listing['original_price'] = price[0].text
							listing['discounted_price'] = price2[0].text
						else:
							listing['discounted_price'] = price[0].text
					except Exception as e:
						logger.exception("Exception while fetching price: ")
						# print("Exception while fetching price: " + str(e))
					info_array = list(filter(lambda a: a != listing['occupancy'] and a != str(listing['original_price']) + listing['discounted_price'] and a != listing['discounted_price'], info_array))

					listing['badges'] = info_array

					key = (listing['name'] + " " + loc + " " + listing['locality']).encode()
					listing['hotel_id'] = hashlib.md5(key).hexdigest()

					print(listing['name'])

					con_ct = 0
					while con_ct < 5:
						try:
							con1 = get_connector()
							if not con1.does_booking_hotel_exist(listing['hotel_id']):
								con1.enter_booking_hotel(listing, loc)
								con1.enter_booking_hotel_photos(listing['hotel_id'], listing['cover_image'])
							else:
								con1.update_booking_hotel(listing)
							con1.enter_booking_hotel_ranking(listing, i, start_date, end_date, loc, today)
							logger.info("Rank: " + str(i))
							print("Rank: " + str(i))
							logger.info("Completed listing: " + listing['name'])
							con_ct = 10

						except Exception as e:
							logger.exception("Exception in add to DB")
							print("Faced excpetion: " + str(e))
							print('\a')
						finally:
							con1.close()
						con_ct = con_ct + 1
					i = i + 1
				except Exception as e:
					print(e)
					print(listing)
					print(li.text)
					print('\a')
					print('\a')
					print('\a')
					logger.error("Error occured during listings.")
					logger.exception("Exception: ")
					logger.error(listing)
					logger.error(info_array)
			driver.close()
			page += 1
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


def fetch_hotel_pages( run_date, start_date):
	for iata in ('STG','STB','NYC','MIL','LAX','HOU','CHI','BOS','AUS','ASP'):
		try:
			# queue = Queue()
			# # Create worker threads
			# for x in range(1):
			# 	worker = DownloadWorker(queue)
			# 	# Setting daemon to True will let the main thread exit even though the workers are blocking
			# 	worker.daemon = True
			# 	worker.start()
			print(iata)
			try:
				con = get_connector()
				hotels = con.get_booking_location(iata)
				location = hotels[0][0]
			except Exception as e:
				print("Initialization failed")
				print(e)
				continue
			finally:
				con.close()
			for h in hotels:
				# queue.put((location, run_date, start_date, start_date + datetime.timedelta(days=1)))
				save_page((location, run_date, start_date, start_date + datetime.timedelta(days=1)))
			# queue.join()
			dir = './test/'
			for f in os.listdir(dir):
			    os.remove(os.path.join(dir, f))
		except:
			logger.exception("Error while running parallel threads")
			print("Error while running parallel threads")


if __name__ == '__main__':
	fetch_hotel_pages( datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d').date(), datetime.datetime.strptime(sys.argv[3], '%Y-%m-%d').date())
	print('\a')
