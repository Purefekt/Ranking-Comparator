import traceback
import undetected_chromedriver as uc
from const import CHROME_VERSION, BOOKING_RAW_REVIEW_DIR
from connector import get_connector
import time
from selenium.webdriver.common.by import By
from datetime import datetime
from utils import *


def get_review_data(review_selenium_object, hotel_id):
    review_info = {
        "review_id": None,
        "brand_type": "BOOKING",
        "reviewer_name": None,
        "country_name": None,
        "type_of_room": None,
        "type_of_room_id": None,
        "number_of_nights": None,
        "stay_month_and_year": None,
        "traveller_type": None,
        "review_date": None,
        "review_title": None,
        "rating": None,
        "pros": None,
        "cons": None,
        "hotel_owner_response": None,
        "number_of_people_found_helpful": None,
        "hotel_id": hotel_id,
        "num_photos": None,
        "reviewers_choice": False
    }

    review_id = review_selenium_object.get_attribute("data-review-url")
    reviewer_name = review_selenium_object.find_elements(By.CSS_SELECTOR, 'span.bui-avatar-block__title')[0].text
    country_name = review_selenium_object.find_elements(By.CSS_SELECTOR, 'span.bui-avatar-block__subtitle')[0].text

    room_info = review_selenium_object.find_elements(By.CSS_SELECTOR, '.c-review-block__room-info-row')[0]
    room_type = room_info.find_elements(By.CSS_SELECTOR, '.bui-list__item')[0].text
    room_type_id = room_info.get_attribute("data-room-id")

    stay_details = review_selenium_object.find_elements(By.CSS_SELECTOR, 'ul.c-review-block__stay-date')[0]
    stay_data = stay_details.find_elements(By.CSS_SELECTOR, "div.bui-list__body")[0].text
    stay_data = stay_data.split('·')
    number_of_nights = stay_data[0].strip()
    stay_month_year = stay_data[1].strip()

    traveller_type_info = review_selenium_object.find_elements(By.CSS_SELECTOR, 'ul.review-panel-wide__traveller_type')[0]
    traveller_type = traveller_type_info.find_elements(By.CSS_SELECTOR, 'div.bui-list__body')[0].text

    review_right_side_block = review_selenium_object.find_elements(By.CSS_SELECTOR, "div.c-review-block__right")[0]
    reviewers_choice = review_right_side_block.find_elements(By.CSS_SELECTOR, "span.c-review-block__badge__icon")
    if len(reviewers_choice) > 0:
        reviewers_choice = True
    else:
        reviewers_choice = False
    review_title = review_right_side_block.find_elements(By.CSS_SELECTOR, ".c-review-block__title")[0].text
    review_date = review_right_side_block.find_elements(By.CSS_SELECTOR, ".c-review-block__date")[0].text
    review_date = review_date.split(':')[1].strip()
    review_date = datetime.strptime(review_date, '%B %d, %Y')
    review_date = review_date.strftime('%Y-%m-%d')
    rating = review_right_side_block.find_elements(By.CSS_SELECTOR, ".bui-review-score__badge")[0].text

    reviews_pro_and_con = review_selenium_object.find_elements(By.CSS_SELECTOR, ".c-review__row")
    review_pro_text = None
    review_con_text = None
    # if there is a single type of review, then it can be good or bad. If there are 2, then first-good and second-bad
    if len(reviews_pro_and_con) == 2:
        review_pro = reviews_pro_and_con[0]
        review_con = reviews_pro_and_con[1]
        review_pro_text = review_pro.find_elements(By.CSS_SELECTOR, ".c-review__body")[0].text
        review_con_text = review_con.find_elements(By.CSS_SELECTOR, ".c-review__body")[0].text

    elif len(reviews_pro_and_con) == 1:
        smiley = reviews_pro_and_con[0].find_elements(By.CSS_SELECTOR, ".c-review__prefix--color-green")
        if len(smiley) > 0:
            review_pro = reviews_pro_and_con[0]
            review_pro_text = review_pro.find_elements(By.CSS_SELECTOR, ".c-review__body")[0].text
        else:
            review_con = reviews_pro_and_con[0]
            review_con_text = review_con.find_elements(By.CSS_SELECTOR, ".c-review__body")[0].text

    helpful = None
    helpful_info = review_selenium_object.find_elements(By.CSS_SELECTOR, ".review-helpful__vote-others-helpful")[0]
    if len(helpful_info.text) > 0:
        helpful = helpful_info.text
        helpful = int(helpful.split(' ')[0])

    owner_response = None
    owner_response_div = review_selenium_object.find_elements(By.CSS_SELECTOR, ".c-review-block__response__inner")
    if len(owner_response_div) > 0:
        owner_response = owner_response_div[0].find_elements(By.CSS_SELECTOR, ".c-review-block__response__body")[0].text

    number_of_photos = None
    photos_links = None
    images_ul_div = review_selenium_object.find_elements(By.CSS_SELECTOR, ".c-review-block__photos")
    if len(images_ul_div) > 0:
        images_list = images_ul_div[0].find_elements(By.CSS_SELECTOR, '.c-review-block__photos__item')
        number_of_photos = len(images_list)
        photos_links = []
        for image in images_list:
            print(image)
            image = image.find_elements(By.CSS_SELECTOR, '.c-review-block__photos__button')[0]
            image_src = image.get_attribute('data-photos-src')
            photos_links.append(image_src)


def save_page(hotel):
    try:
        opts = uc.ChromeOptions()
        opts.headless = True
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        driver = uc.Chrome(version_main=CHROME_VERSION, suppress_welcome=False, options=opts)

        url = hotel[1]
        print(f'Processing hotel --> {hotel[0]}')
        if '?' in url:
            url = url[:url.index('?')]
        driver.get(url)

        time.sleep(4)

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
        # press continue reading for all owner replies in a page
        continue_reading_button = driver.find_elements(By.CSS_SELECTOR,'a[data-component="ugcs/dom-utils/toggle prevent-default-helper"]')
        for button in continue_reading_button:
            button.click()

        for review in first_page_reviews:
            get_review_data(review, hotel[0])

        send_raw_file(driver.page_source, BOOKING_RAW_REVIEW_DIR + '1_TRY/', hotel[0] + '_page1.html.gz')

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
            time.sleep(3)
            # press continue reading for all owner replies in a page
            continue_reading_button = driver.find_elements(By.CSS_SELECTOR,'a[data-component="ugcs/dom-utils/toggle prevent-default-helper"]')
            for button in continue_reading_button:
                button.click()
            next_page_button = driver.find_elements(By.CSS_SELECTOR, 'a.pagenext')
            num_pages += 1
            send_raw_file(driver.page_source, BOOKING_RAW_REVIEW_DIR + '1_TRY/', hotel[0] + '_page' + str(num_pages) +'.html.gz')
            print(f'    On page number -> {num_pages}')
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

# hotels = [
#     ('0003faac0e04e1fba74d01e6895e4b18', 'https://www.booking.com/hotel/us/sweet-home-alabama-street-in-houston-central.html?aid=304142&ucfs=1&arphpl=1&checkin=2022-06-18&checkout=2022-06-19&dest_id=20128761&dest_type=city&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=426&sr_order=popularity&srpvid=84c9051f875100d9&srepoch=1655513023&all_sr_blocks=636592001_335200376_6_0_0&highlighted_blocks=636592001_335200376_6_0_0&matching_block_id=636592001_335200376_6_0_0&sr_pri_blocks=636592001_335200376_6_0_0__22200&tpi_r=2&from=searchresults#hotelTmpl'),
#     ('00aa4734d9c6d26830fd291b98087b34', 'https://www.booking.com/hotel/us/courtyard-houston-brookhollow.html?aid=304142&ucfs=1&arphpl=1&checkin=2022-06-17&checkout=2022-06-18&dest_id=20128761&dest_type=city&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=17&hapos=292&sr_order=popularity&srpvid=94f602affde5015c&srepoch=1655511776&all_sr_blocks=18102007_91825624_0_34_0&highlighted_blocks=18102007_91825624_0_34_0&matching_block_id=18102007_91825624_0_34_0&sr_pri_blocks=18102007_91825624_0_34_0__8560&tpi_r=2&from=searchresults#hotelTmpl'),
#     ('000b844cb054f24182710897d78ac640', 'https://www.booking.com/hotel/us/modern-one-bedroom-located-in-the-texas-medical-center.html?aid=304142&label=gen173nr-1FCAQoggJCDWNpdHlfMjAxMjg3NjFIM1gEaIkCiAEBmAExuAEHyAEM2AEB6AEB-AEDiAIBqAIDuALxoPaeBsACAdICJDA2NTUyYTg5LTg1MjUtNDM4Yy1hNTIxLWRjZjhjOGIwNjFjONgCBeACAQ&ucfs=1&arphpl=1&checkin=2023-02-05&checkout=2023-02-06&dest_id=20128761&dest_type=city&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=9&hapos=234&sr_order=popularity&srpvid=59a9a0f8bff201a2&srepoch=1675464818&all_sr_blocks=956790801_368318576_4_0_0&highlighted_blocks=956790801_368318576_4_0_0&matching_block_id=956790801_368318576_4_0_0&sr_pri_blocks=956790801_368318576_4_0_0__18000&from=searchresults#hotelTmpl')
# ]

hotels = [
    ('00a7b1a690f401a00e52e0b17e6d75cc', 'https://www.booking.com/hotel/us/hilton-garden-inn-times-square-central.html?aid=304142&ucfs=1&arphpl=1&checkin=2022-06-18&checkout=2022-06-19&dest_id=20088325&dest_type=city&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=6&hapos=31&sr_order=popularity&srpvid=bb26895938dd0422&srepoch=1655580723&all_sr_blocks=61792902_266277720_2_2_0&highlighted_blocks=61792902_266277720_2_2_0&matching_block_id=61792902_266277720_2_2_0&sr_pri_blocks=61792902_266277720_2_2_0__27900&from_sustainable_property_sr=1&from=searchresults#hotelTmpl')]


for hotel in hotels:
    save_page(hotel)
