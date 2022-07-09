from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chromium.options import ChromiumOptions
import undetected_chromedriver as uc

import datetime
import os
import time
from urllib.parse import urlencode

EXPEDIA_SEARCH_URL = 'https://www.expedia.com/Hotel-Search?'


def scrape(loc, start_date, end_date, today):
	try:
		listing = None
		query = {
			"endDate": str(end_date),
			"startDate": str(start_date)
		}
		print("Checking location: " + loc[0])
		query["destination"] = loc[0]
		query["regionId"] = loc[1]

		opts = uc.ChromeOptions()
		opts.headless = True
		opts.add_argument('--headless')
		# opts.add_argument("--start-maximized")
		# opts = ChromiumOptions()
		# opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36")
		# opts.add_argument("--incognito")
		# driver = webdriver.Chrome(executable_path=os.path.abspath('./chromedriver'), chrome_options=opts)
		driver = uc.Chrome(suppress_welcome=False, options=opts)
		url = EXPEDIA_SEARCH_URL + urlencode(query)
		print(url)
		driver.get(url)
		time.sleep(5)
		# driver.set_window_size(width=1200, height=831)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
		time.sleep(1)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)

		ct = 100
		try:
			while driver.find_elements(By.CSS_SELECTOR, '.uitk-spacing-padding-blockstart-three .uitk-button-secondary'):
				listings = driver.find_elements(By.CSS_SELECTOR, '.uitk-spacing.uitk-spacing-margin-blockstart-three')
				print("Found listings: " + str(len(listings)))
				if len(listings) == ct:
					break
				ct = len(listings)
				next_page_button = driver.find_element(By.CSS_SELECTOR, '.uitk-spacing-padding-blockstart-three .uitk-button-secondary')
				if next_page_button.is_enabled():
					next_page_button.click()
					time.sleep(5)

				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(2)

				# driver.set_window_size(width=800, height=831)
				# driver.set_window_size(width=1200, height=831)
				# time.sleep(5)
		except:
			pass
	except:
		print(listing['name'])
		print(listing)
		print('\a')
		print('\a')
		print('\a')
		print('\a')
		print('\a')
	finally:
		driver.close()


if __name__ == '__main__':
	today = datetime.date.today()
	loc = ['Los Angeles (and vicinity), California, United States of America', '178280']
	scrape(loc, today, today + datetime.timedelta(days=1), today)
