import time
from connector import get_connector
import undetected_chromedriver as uc
from const import BOOKING_RAW_HOTEL_DIR, CHROME_VERSION
from selenium.webdriver.common.by import By
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="geoapiExercises")
import json
import traceback
from utils import *
from threading import Thread
from queue import Queue


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
                print("Error before processing")


def save_page(hotel):
    try:
        opts = uc.ChromeOptions()
        opts.headless = True
        opts.add_argument('--headless')
        driver = uc.Chrome(version_main=CHROME_VERSION, suppress_welcome=False, options=opts)

        url = hotel[1]
        print(f'Processing hotel --> {hotel[0]}')
        if '?' in url:
            url = url[:url.index('?')]
        driver.get(url)

        time.sleep(6)

        send_raw_file(driver.page_source, BOOKING_RAW_HOTEL_DIR + '1_TRY/', hotel[0] + '.html.gz')

        try:
            hotel_info = {
                "hotel_id": hotel[0],
                "url": url,
                "country": None,
                "latitude": None,
                "locality": None,
                "longitude": None,
                "postal_code": None,
                "region": None,
                "street_address": None,
                "title": None,
                "description": None
            }

            hotel_info["title"] = driver.find_elements(By.XPATH, '//*[@id="hp_hotel_name"]/div/h2')[0].text

            lat_lng_script_element = driver.find_elements(By.XPATH, "//script[contains(text(),'booking.env.b_map_center_latitude')]")[0]
            lat_lng_text = lat_lng_script_element.get_attribute("innerHTML").split('=')
            hotel_info["latitude"] = str(lat_lng_text[1].split(';')[0][1:])
            hotel_info["longitude"] = str(lat_lng_text[2].split(';')[0][1:])
            hotel_info["country"] = geolocator.reverse(hotel_info["latitude"] + "," + hotel_info["longitude"]).raw['address'].get('country')

            address_script_element = driver.find_elements(By.XPATH, "//script[contains(text(),'addressCountry')]")[0]
            address_text = address_script_element.get_attribute("innerHTML")
            address_dict = json.loads(address_text)
            hotel_info["locality"] = address_dict["address"]["addressLocality"]
            postal_code_tmp = address_dict["address"]["postalCode"].split(' ')
            if len(postal_code_tmp) > 1:
                for item in postal_code_tmp:
                    if item.isnumeric():
                        hotel_info["postal_code"] = str(item)
            else:
                hotel_info["postal_code"] = str(postal_code_tmp[0])
            hotel_info["region"] = address_dict["address"]["addressRegion"]
            hotel_info["street_address"] = address_dict["address"]["streetAddress"]

            hotel_info["description"] = driver.find_elements(By.ID, 'property_description_content')[0].text

        except Exception as e:
            if 'list index out of range' in str(e):
                try:
                    con = get_connector()
                    con.mark_booking_hotel_incomplete(hotel[0])
                    con.close()
                except Exception as ep:
                    print(ep)
                    return
            print(e)
            return

        try:
            con = get_connector()
            con.enter_booking_hotel_info(hotel_info)
            con.mark_booking_hotel_info_complete(hotel[0])
            con.close()
        except Exception as e:
            traceback.print_exc()
            print(e)
            print('SQL connection failed')
            driver.close()
            return

    except Exception as e:
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
    try:
        queue = Queue()
        # Create worker threads
        for x in range(6):
            worker = DownloadWorker(queue)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()
        try:
            con = get_connector()
            hotels = con.get_booking_hotel_urls()
            print("Number of hotels: " + str(len(hotels)))
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
        print("Error while running parallel threads")

if __name__ == '__main__':
	fetch_hotel_pages()
	print('\a')

