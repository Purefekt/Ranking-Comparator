from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

import hashlib
import os
import time
from urllib.parse import urlencode

# from requester import generic_request
from connector import connector
from const import BOOKING_SEARCH_URL, BOOKING_RAW_DIR
from logger import logger
from utils import *


def fetch_rankings(start_date, end_date, today):
	try:

		query = {
			"checkout_year": str(end_date.year),
			"checkin_year": str(start_date.year),
			"checkout_month": str(end_date.month),
			"checkin_month": str(start_date.month),
			"checkout_monthday": str(end_date.day),
			"checkin_monthday": str(start_date.day),
			"group_adults": 2,
			"group_children": 0,
			"no_rooms": 1
		}
		locations = connector.get_booking_locations()
		for loc in locations:
			# logger.info("Checking location: " + loc[0])
			print()
			print("Checking location: " + loc[0])
			query["ss"] = loc[0]
			query["dest_id"] = loc[1]
			query["dest_type"] = loc[2]

			limit = 500
			offset = 0
			page = 1
			i = 1

			while offset < limit:
				query["offset"] = offset

				url = BOOKING_SEARCH_URL + urlencode(query)
				logger.info("URl: " + url)
				print(url)

				# response = generic_request(url, '', url_params=None, with_proxy=True)
				# time.sleep(5)
				# page = response.content
				# with open('a.html', 'w') as f:
				# 	f.write(page.decode())
				# f.close()
				# soup = BeautifulSoup(page, 'html.parser')
				# # listings = soup.findAll('div', {'class': 'dcf496a7b9'})
				# # print(len(listings))
				# return

				# chrome_driver = os.environ.get('CHROME_DRIVER')
				# driver = webdriver.Chrome(executable_path=chrome_driver)
				# driver = webdriver.Safari()
				# driver = webdriver.Firefox(executable_path="./../geckodriver")
				opts = uc.ChromeOptions()
				opts.headless = True
				opts.add_argument('--headless')
				driver = uc.Chrome(suppress_welcome=False, options=opts)

				driver.get(url)
				time.sleep(6)

				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(1)

				# save_raw_file(driver.page_source, BOOKING_RAW_DIR + 'RUNDATE_' + str(datetime.date.today()) + '/' + loc[0] + '/' + str(start_date) + '__' + str(end_date) + '/', 'page' + str(page) + '.html.gz')
				save_raw_file(driver.page_source, BOOKING_RAW_DIR + 'RUNDATE_' + str(today) + '/' + loc[0] + '/' + str(start_date) + '__' + str(end_date) + '/', 'page' + str(page) + '.html.gz')

				total_listing = driver.find_elements(By.XPATH, "//h1")
				if len(total_listing) > 0:
					ct = total_listing[0].text
					limit = int(ct[ct.index(':') + 2:-17].replace(',', ''))
					# logger.info('Total listings' + str(limit))
					# print('Total listings' + str(limit))

				listings = driver.find_elements(By.XPATH, "//div[@data-testid='property-card']")
				# logger.info("Found listing: " + str(len(listings)))
				# print("Found listings: " + str(len(listings)))
				for li in listings:

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
						'original_price': None,
						'discounted_price': None,
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
						# logger.exception("recommended-unit now found: ")
						pass

					occupancy = li.find_elements(By.CSS_SELECTOR, "div[data-testid='price-for-x-nights']")
					if len(occupancy) > 0:
						listing['occupancy'] = occupancy[0].text
					price = li.find_elements(By.CSS_SELECTOR, "div[data-testid='price-and-discounted-price'] > span:nth-child(1)")
					price2 = li.find_elements(By.CSS_SELECTOR, "div[data-testid='price-and-discounted-price'] > span:nth-child(2)")
					if len(price2) > 0:
						listing['original_price'] = price[0].text
						listing['discounted_price'] = price2[0].text
					else:
						listing['discounted_price'] = price[0].text
					info_array = list(filter(lambda a: a != listing['occupancy'] and a != str(listing['original_price']) + listing['discounted_price'] and a != listing['discounted_price'], info_array))

					listing['badges'] = info_array

					# print(info_array)

					key = (listing['name'] + " " + loc[0] + " " + listing['locality']).encode()
					listing['hotel_id'] = hashlib.md5(key).hexdigest()

					# logger.info("Hotel name: " + listing['name'])
					print(listing['name'])
					# logger.info(listing)

					if not connector.does_booking_hotel_exist(listing['hotel_id']):
						connector.enter_booking_hotel(listing, loc[0])
						connector.enter_booking_hotel_photos(listing['hotel_id'], listing['cover_image'])
					else:
						# logger.info("Hotel already exists. Please check. " + listing['name'])
						# print("################# Hotel already exists. Please check. " + listing['name'])
						connector.update_booking_hotel(listing)
					connector.enter_booking_hotel_ranking(listing, i, start_date, end_date, loc[0], today)
					logger.info("Rank: " + str(i))
					print("Rank: " + str(i))
					logger.info("Completed listing: " + listing['name'])
					i = i + 1
				offset = offset + 25
				page = page + 1
			logger.info("First Location complete.")
			print("First Location complete.")
			print()
			print()
	except:
		logger.error(" Booking Error occured.")
		logger.exception("Exception: ")
		print(listing)
		print(li.text)
		print('\a')
		print('\a')
		print('\a')
		print('\a')
		print('\a')
		print('\a')
		logger.error(listing)
		logger.error(info_array)
		raise
