from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import undetected_chromedriver as uc
import time
import os
from logger import logger as logging

def get_chrome_main_version():
    chrome_path = uc.find_chrome_executable()
    print(chrome_path)
    bare_version = os.popen(f"{chrome_path} --version").read()
    return bare_version.strip("Google Chrome").split('.')[0]

def scrape_uc():
	try:
# #		print(uc.find_chrome_executable())
# 		logging.info(uc.find_chrome_executable())
#		time.sleep(50)
		opts = uc.ChromeOptions()
		# opts.arguments.extend(["--no-sandbox", "--disable-setuid-sandbox"])
		# opts.add_argument('--user-data-dir=/tmp/dvdsdsfdummyprofile')
		# options.arguments.extend(["--no-sandbox", "--disable-setuid-sandbox"])
		# opts.add_argument("--incognito")
		logging.info("Here")
		driver = uc.Chrome(headless=True, version_main=106, options=opts, service_args=["--verbose", "--log-path=cd.log"])

		driver.get('https://myexternalip.com/raw')
		print(driver.find_elements(By.CSS_SELECTOR, 'body')[0].text)
		time.sleep(1)
		logging.info(driver.find_elements(By.CSS_SELECTOR, "body")[0].text)
	except Exception as e:
#		print("hel" + str(e))
		logging.exception("Exception occured: ")


def scrape_s():
	try:
		logging.info("Here")
		options = Options()
		options.headless = True
		driver = webdriver.Chrome('./chromedriver', options=options)
		driver.get('https://myexternalip.com/raw')
		print(driver.find_elements(By.CSS_SELECTOR, 'body')[0].text)
		time.sleep(1)
		logging.info(driver.find_elements(By.CSS_SELECTOR, "body")[0].text)
	except Exception as e:
#		print("hel" + str(e))
		logging.exception("Exception occured: ")

if __name__ == '__main__':
	# get_chrome_main_version()
	scrape_s()