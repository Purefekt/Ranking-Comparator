import traceback
import undetected_chromedriver as uc
from const import CHROME_VERSION
from connector import get_connector
import time
from selenium.webdriver.common.by import By


def save_page(hotel):
    try:
        opts = uc.ChromeOptions()
        # opts.headless = True
        # opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        driver = uc.Chrome(version_main=CHROME_VERSION, suppress_welcome=False, options=opts)

        url = hotel[1]
        print(f'Processing hotel --> {hotel[0]}')
        if '?' in url:
            url = url[:url.index('?')]
        driver.get(url)

        time.sleep(4)

        """SEND RAW FILE COMES HERE"""

        # click the reviews button. Note: This works for when there are no reviews as well for some reason
        all_reviews_button = driver.find_elements(By.CSS_SELECTOR, "li.a0661136c9 a[href='#blockdisplay4']")[0]
        all_reviews_button.click()

        # check if there are no reviews. If none then mark this hotel as 3 in booking_hotels -> flag_reviews
        no_reviews_box = driver.find_elements(By.CSS_SELECTOR, "div.not_enough_reviews")
        if len(no_reviews_box) > 0:
            try:
                con = get_connector()
                con.mark_booking_hotel_no_reviews_found(hotel[0])
                con.close()
            except Exception as e:
                traceback.print_exc()
                print('SQL connection failed')
                print(e)
            finally:
                return

        # Get all the reviews from the first page. Then move to the bottom and move to the 2nd page if it exists
        ALL_REVIEWS = []
        driver.set_window_size(width=1200, height=831)
        time.sleep(0.5)

        first_page_reviews = driver.find_elements(By.CSS_SELECTOR, 'li.review_list_new_item_block')
        for review in first_page_reviews:
            print(review)

        # move to the 2nd page and get all the reviews. Repeat this till next page exists
        next_page_button = driver.find_elements(By.CSS_SELECTOR, 'a.pagenext')
        num_pages = 1

        while next_page_button:
            # scroll to the bottom and press the next page button if it exists. For each page get all reviews info
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
            time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            next_page_button[0].click()
            time.sleep(1)
            next_page_button = driver.find_elements(By.CSS_SELECTOR, 'a.pagenext')
            num_pages += 1
        print(f'Number of pages -> {num_pages}')








    except Exception as e:
        print('=======================================================================================================\
        =========================================================================================')
        traceback.print_exc()
        print(e)
        print('\a')
        print('\a')
        print('\a')
        print('\a')
        print('\a')
    finally:
        driver.close()

# RUN
# con = get_connector()
# hotels = con.get_booking_hotels_urls_for_reviews()
# print("Number of hotels: " + str(len(hotels)))

hotels = [
    ('0003faac0e04e1fba74d01e6895e4b18', 'https://www.booking.com/hotel/us/sweet-home-alabama-street-in-houston-central.html?aid=304142&ucfs=1&arphpl=1&checkin=2022-06-18&checkout=2022-06-19&dest_id=20128761&dest_type=city&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=426&sr_order=popularity&srpvid=84c9051f875100d9&srepoch=1655513023&all_sr_blocks=636592001_335200376_6_0_0&highlighted_blocks=636592001_335200376_6_0_0&matching_block_id=636592001_335200376_6_0_0&sr_pri_blocks=636592001_335200376_6_0_0__22200&tpi_r=2&from=searchresults#hotelTmpl'),
    ('00aa4734d9c6d26830fd291b98087b34', 'https://www.booking.com/hotel/us/courtyard-houston-brookhollow.html?aid=304142&ucfs=1&arphpl=1&checkin=2022-06-17&checkout=2022-06-18&dest_id=20128761&dest_type=city&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=17&hapos=292&sr_order=popularity&srpvid=94f602affde5015c&srepoch=1655511776&all_sr_blocks=18102007_91825624_0_34_0&highlighted_blocks=18102007_91825624_0_34_0&matching_block_id=18102007_91825624_0_34_0&sr_pri_blocks=18102007_91825624_0_34_0__8560&tpi_r=2&from=searchresults#hotelTmpl'),
    ('000b844cb054f24182710897d78ac640', 'https://www.booking.com/hotel/us/modern-one-bedroom-located-in-the-texas-medical-center.html?aid=304142&label=gen173nr-1FCAQoggJCDWNpdHlfMjAxMjg3NjFIM1gEaIkCiAEBmAExuAEHyAEM2AEB6AEB-AEDiAIBqAIDuALxoPaeBsACAdICJDA2NTUyYTg5LTg1MjUtNDM4Yy1hNTIxLWRjZjhjOGIwNjFjONgCBeACAQ&ucfs=1&arphpl=1&checkin=2023-02-05&checkout=2023-02-06&dest_id=20128761&dest_type=city&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=9&hapos=234&sr_order=popularity&srpvid=59a9a0f8bff201a2&srepoch=1675464818&all_sr_blocks=956790801_368318576_4_0_0&highlighted_blocks=956790801_368318576_4_0_0&matching_block_id=956790801_368318576_4_0_0&sr_pri_blocks=956790801_368318576_4_0_0__18000&from=searchresults#hotelTmpl')
]


for hotel in hotels:
    save_page(hotel)
