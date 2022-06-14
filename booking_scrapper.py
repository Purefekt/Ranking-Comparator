from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

import hashlib
import os
import time
from urllib.parse import urlencode

from requester import generic_request
from connector import connector
from const import BOOKING_SEARCH_URL
from logger import logger
from utils import *


def fetch_rankings(start_date, end_date):
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
		logger.info("Checking location: " + loc[0])
		print("Checking location: " + loc[0])
		query["ss"] = loc[0]
		query["dest_id"] = loc[1]
		query["dest_type"] = loc[2]

		limit = 200
		offset = 0
		i = 0

		while offset <= limit:
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

			chrome_driver = os.environ.get('CHROME_DRIVER')
			driver = webdriver.Chrome(executable_path=chrome_driver)
			driver.get(url)
			time.sleep(7)

			total_listing = driver.find_elements(By.CSS_SELECTOR, "div[data-capla-componenet='b-search-web-searchresults/HeaderDesktop']")
			if len(total_listing) > 0:
				print(total_listing[0].text)
				offset = min(limit, int(total_listing[0].text))

			listings = driver.find_elements(By.XPATH, "//div[@data-testid='property-card']")
			logger.info("Found listing: " + str(len(listings)))
			print("Found listings: " + str(len(listings)))
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

				listing['locality'] = li.find_elements(By.CSS_SELECTOR, "span[data-testid='address']")[0].text
				listing['distance_from_center'] = li.find_elements(By.CSS_SELECTOR, "span[data-testid='distance']")[0].text[:-18]
				location = li.find_elements(By.CSS_SELECTOR, "div[data-testid='location']")[0]
				listing['map_url'] = location.find_elements(By.CSS_SELECTOR, "div > a")[0].get_attribute("href")
				listing['location_addon'] = location.text[location.text.index(' miles from center') + 18:]
				info_array = list(filter(lambda a: a != location.text, info_array))

				rating = li.find_elements(By.CSS_SELECTOR, "div[data-testid='review-score']")[0]
				listing['rating'] = rating.find_elements(By.CSS_SELECTOR, "div > div:nth-child(1)")[0].text
				listing['comment'] = rating.find_elements(By.CSS_SELECTOR, "div > div:nth-child(2) > div:nth-child(1)")[0].text
				listing['review_count'] = rating.find_elements(By.CSS_SELECTOR, "div > div:nth-child(2) > div:nth-child(2)")[0].text
				info_array = list(filter(lambda a: a != listing['rating'] and a != listing['comment'] and a != listing['review_count'], info_array))
				listing['review_count'] = listing['review_count'][:-8].replace(',', '')

				rec_unit = li.find_elements(By.CSS_SELECTOR, "div[data-testid='recommended-units']")[0]
				listing['recommended-unit'] = rec_unit.find_elements(By.CSS_SELECTOR, " div > div > div > div:nth-child(1) > span")[0].text
				listing['recommended-unit-beds'] = rec_unit.find_elements(By.CSS_SELECTOR, " div > div > div > div:nth-child(2)")[0].text
				availability = rec_unit.find_elements(By.CSS_SELECTOR, " div > div > div > div:nth-child(3)")
				if len(availability) > 0:
					listing['availability'] = availability[0].text
				info_array = list(filter(lambda a: a != listing['recommended-unit'] and a != listing['recommended-unit-beds'] and a != listing['availability'], info_array))

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
				info_array = list(filter(lambda a: a != listing['occupancy'] and a != listing['original_price'] and a != listing['discounted_price'], info_array))

				listing['badges'] = info_array

				print(info_array)

				key = (listing['name'] + " " + loc[0] + " " + listing['locality']).encode()
				listing['hotel_id'] = hashlib.md5(key).hexdigest()

				logger.info("Hotel name: " + listing['name'])
				print("Hotel name: " + listing['name'])
				logger.info(listing)

				if not connector.does_booking_hotel_exist(listing['hotel_id']):
					connector.enter_booking_hotel(listing, loc[0])
					connector.enter_booking_hotel_photos(listing['hotel_id'], listing['cover_image'])
				else:
					print("Hotel already exists. Please check. ")
					connector.update_booking_hotel(listing)
				connector.enter_booking_hotel_ranking(listing, i, start_date, end_date, loc[0])
				i = i + 1
			time.sleep(1000)
			return
			offset = offset + 25
		logger.info("First Location complete.")
		print("First Location complete.")
