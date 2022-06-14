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

from connector import connector
from const import EXPEDIA_SEARCH_URL
from logger import logger
from utils import *


def fetch_rankings(start_date, end_date):
	query = {
		"endDate": str(end_date),
		"startDate": str(start_date)
	}
	locations = connector.get_expedia_locations()
	for loc in locations:
		logger.info("Checking location: " + loc[0])
		print("Checking location: " + loc[0])
		query["destination"] = loc[0]
		query["regionId"] = loc[1]

		chrome_driver = os.environ.get('CHROME_DRIVER')
		driver = webdriver.Chrome(executable_path=chrome_driver)
		url = EXPEDIA_SEARCH_URL + urlencode(query)
		logger.info("URl: " + url)
		print(url)
		driver.get(url)
		time.sleep(7)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
		time.sleep(5)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(5)

		next_page_button = driver.find_element(By.CSS_SELECTOR, '.uitk-spacing-padding-blockstart-three .uitk-button-secondary')
		if next_page_button.is_enabled():
			print("here:")
			next_page_button.click()
			time.sleep(10)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
		time.sleep(5)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(5)

		listings = driver.find_elements(By.CSS_SELECTOR, '.uitk-spacing.uitk-spacing-margin-blockstart-three')
		logger.info("Found listing: " + str(len(listings)))
		print("Found listings: " + str(len(listings)))
		i = 0
		for li in listings:
			if i == 0:
				i = i + 1
				continue
			name_element = li.find_elements(By.CSS_SELECTOR, "li > h3")
			photo_gallery = li.find_elements(By.CSS_SELECTOR, ".uitk-image-media")
			access = li.find_elements(By.CSS_SELECTOR, ".uitk-badge-vip")
			# nbh_element = li.find_elements(By.CSS_SELECTOR, "li > div > div > div.uitk-card-content-section.uitk-card-content-section-padded.uitk-layout-grid-item.listing-content.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div")
			review_element = li.find_elements(By.CSS_SELECTOR, "li > div > div > div.uitk-card-content-section.uitk-card-content-section-padded.uitk-layout-grid-item.uitk-layout-grid-item-columnspan > div > div.uitk-layout-grid.uitk-layout-grid-columns-3.uitk-layout-flex-item.uitk-layout-flex-item-flex-grow-1 > div.uitk-layout-grid-item.uitk-layout-grid-item-align-self-end.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div > div > span:nth-child(1) ")
			comment_element = li.find_elements(By.CSS_SELECTOR, "li > div > div > div.uitk-card-content-section.uitk-card-content-section-padded.uitk-layout-grid-item.listing-content.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div > div.uitk-layout-grid.uitk-layout-grid-align-content-end.uitk-layout-grid-columns-3.uitk-layout-flex-item.uitk-layout-flex-item-flex-grow-1 > div.uitk-layout-grid-item.uitk-layout-grid-item-align-self-end.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div.listing__reviews.all-t-margin-two > div > span:nth-child(1) > span.uitk-type-300.pwa-theme--grey-700.all-r-padding-one")
			review_count_element = li.find_elements(By.CSS_SELECTOR, "li > div > div > div.uitk-card-content-section.uitk-card-content-section-padded.uitk-layout-grid-item.listing-content.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div > div.uitk-layout-grid.uitk-layout-grid-align-content-end.uitk-layout-grid-columns-3.uitk-layout-flex-item.uitk-layout-flex-item-flex-grow-1 > div.uitk-layout-grid-item.uitk-layout-grid-item-align-self-end.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div.listing__reviews.all-t-margin-two > div > span:nth-child(1) > span.pwa-theme--grey-700[data-stid='content-hotel-reviews-total']")
			full_review_element = li.find_elements(By.CSS_SELECTOR, "li > div > div > div.uitk-card-content-section.uitk-card-content-section-padded.uitk-layout-grid-item.listing-content.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div > div.uitk-layout-grid.uitk-layout-grid-align-content-end.uitk-layout-grid-columns-3.uitk-layout-flex-item.uitk-layout-flex-item-flex-grow-1 > div.uitk-layout-grid-item.uitk-layout-grid-item-align-self-end.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div.listing__reviews.all-t-margin-two > div > span:nth-child(2)")
			badge_element = li.find_elements(By.CSS_SELECTOR, "span.uitk-badge")
			urls_element = li.find_elements(By.CSS_SELECTOR, "li > div > a")
			total_price_element = li.find_elements(By.CSS_SELECTOR, "li > div > div > div.uitk-card-content-section.uitk-card-content-section-padded.uitk-layout-grid-item.listing-content.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div > div.uitk-layout-grid.uitk-layout-grid-align-content-end.uitk-layout-grid-columns-3.uitk-layout-flex-item.uitk-layout-flex-item-flex-grow-1 > div.uitk-layout-grid-item.uitk-layout-grid-item-align-self-end.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-1.uitk-layout-grid-item-justify-self-end > div > div > div:nth-child(2) > div")
			price_element = li.find_elements(By.CSS_SELECTOR, "li > div > div > div.uitk-card-content-section.uitk-card-content-section-padded.uitk-layout-grid-item.listing-content.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div > div.uitk-layout-grid.uitk-layout-grid-align-content-end.uitk-layout-grid-columns-3.uitk-layout-flex-item.uitk-layout-flex-item-flex-grow-1 > div.uitk-layout-grid-item.uitk-layout-grid-item-align-self-end.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-1.uitk-layout-grid-item-justify-self-end > div > div > div:nth-child(1) > div > span")
			old_price_element = li.find_elements(By.CSS_SELECTOR, "li > div > div > div.uitk-card-content-section.uitk-card-content-section-padded.uitk-layout-grid-item.listing-content.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-2 > div > div.uitk-layout-grid.uitk-layout-grid-align-content-end.uitk-layout-grid-columns-3.uitk-layout-flex-item.uitk-layout-flex-item-flex-grow-1 > div.uitk-layout-grid-item.uitk-layout-grid-item-align-self-end.uitk-layout-grid-item-columnspan.uitk-layout-grid-item-columnspan-1.uitk-layout-grid-item-justify-self-end > div > div > div:nth-child(1) > button > div > div > del > span")

			info_array = li.text.splitlines()

			# Removing excess info
			for a in info_array:
				if a.startswith("Photo gallery"):
					info_array.remove(a)
					break
			for a in info_array:
				if a == 'Primary image':
					info_array.remove(a)
					break
			for a in info_array:
				if a.startswith('Save') and a.endswith('to your lists'):
					info_array.remove(a)
					break
			for a in info_array:
				if a.startswith('More information about'):
					info_array.remove(a)
					break

			listing = {
				'hotel_id': None,
				'name': None,
				'nbh': None,
				'rating': None,
				'comment': None,
				'review_count': None,
				'full_review': None,
				'original_price': None,
				'price': None,
				'total_price': None,
				'url': None,
				'conflict': False,
				'sponsored': False,
				'vip_access': None,
				'url': None,
				'amenities': None
			}

			# Name of the hotel
			for n in name_element:
				listing['name'] = n.text
			tmp = info_array[0]
			listing['name'] = compare(listing['name'], tmp, listing)
			info_array = list(filter(lambda a: a != tmp, info_array))

			# Photo Gallery
			listing['photos'] = [photo.get_attribute("src") for photo in photo_gallery]

			# VIP Access
			listing['vip_access'] = None
			if(len(access) == 1):
				listing['vip_access'] = access[0].text
			for a in info_array:
				if a == 'VIP Access':
					listing['vip_access'] = a
					info_array.remove(a)
					break

			# URL
			for u in urls_element:
				listing['url'] = u.get_attribute("href")

			# Badges
			listing['badges'] = [badge.text for badge in badge_element]
			if 'Ad' in listing['badges']:
				listing['sponsored'] = True
				listing['badges'].remove('Ad')
			for a in info_array:
				if a == 'Ad':
					listing['sponsored'] = True
					info_array.remove(a)
					break
			info_array = list(filter(lambda a: a not in listing['badges'], info_array))

			# Price
			for op in old_price_element:
				listing['original_price'] = op.text
			for a in info_array:
				if a.startswith("The price was"):
					tmp = a[14:]
					listing['original_price'] = compare(listing['original_price'], tmp, listing)
					info_array.remove(a)
					info_array.remove(tmp)
					break
			for p in price_element:
				listing['price'] = p.text
			for a in info_array:
				if a.startswith("The price is"):
					tmp = a[13:]
					listing['price'] = compare(listing['price'], tmp, listing)
					info_array.remove(a)
					info_array.remove(tmp)
					break
			for tp in total_price_element:
				listing['total_price'] = tp.text[:-6]
			for a in info_array:
				if a.endswith("total") and a.startswith("$"):
					tmp = a[:-6]
					listing['total_price'] = compare(listing['total_price'], tmp, listing)
					info_array.remove(a)
					break

			# Review
			if(len(review_element) > 0):
				listing['rating'] = review_element[0].text
			if(len(comment_element) > 0):
				listing['comment'] = comment_element[0].text
			if(len(review_count_element) > 0):
				listing['review_count'] = int(review_count_element[0].text[1:-9].replace(',', ''))
			if(len(full_review_element) > 0):
				listing['full_review'] = full_review_element[0].text
			for a in info_array:
				if a.endswith("reviews)") and "out of 5" in a:
					listing['rating'] = compare(listing['rating'], a[:a.index(" out of 5")] + '/5', listing)
					listing['comment'] = compare(listing['comment'], a[a.index(" out of 5") + 9:a.index('(') - 1], listing)
					listing['review_count'] = compare(listing['review_count'], int(a[a.index('(') + 1:a.index(' reviews)')].replace(',', '')), listing)
					listing['full_review'] = compare(listing['full_review'], a, listing)
					info_array.remove(a)
					info_array.remove(a.replace(' 5 ', ' 5').replace(' out of ', '/').replace(' (', '('))

			listing['nbh'] = info_array[0]
			info_array.pop(0)
			listing['amenities'] = info_array

			listing['full_text'] = li.text

			logger.info("Hotel name: " + listing['name'])
			logger.info(listing)

			key = (listing['name'] + " " + loc[0] + " " + listing['nbh']).encode()
			listing['hotel_id'] = hashlib.md5(key).hexdigest()

			print(listing['name'])
			print(listing['hotel_id'])
			if not connector.does_expedia_hotel_exist(listing['hotel_id']):
				connector.enter_expedia_hotel(listing, loc[0])
				connector.enter_expedia_hotel_photos(listing['hotel_id'], listing['photos'])
			else:
				print("Hotel already exists. Please check. ")
				connector.update_expedia_hotel(listing)
			connector.enter_expedia_hotel_ranking(listing, i, start_date, end_date, loc[0])
			i = i + 1
		logger.info("First Location complete.")
		print("First Location complete.")
