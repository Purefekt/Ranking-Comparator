import traceback
import undetected_chromedriver as uc
from const import CHROME_VERSION
from connector import get_connector
import time
from selenium.webdriver.common.by import By
from datetime import datetime
import json
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
                print('Error before processing')


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
        "reviewers_choice": False,
        "photos_links": None
    }

    review_id = review_selenium_object.get_attribute("data-review-url")

    reviewer_name = None
    reviewer_name_element = review_selenium_object.find_elements(By.CSS_SELECTOR, 'span.bui-avatar-block__title')
    if len(reviewer_name_element) > 0:
        reviewer_name = reviewer_name_element[0].text

    country_name = None
    country_name_element = review_selenium_object.find_elements(By.CSS_SELECTOR, 'span.bui-avatar-block__subtitle')
    if len(country_name_element) > 0:
        country_name = country_name_element[0].text

    room_type = None
    room_type_id = None
    room_info = review_selenium_object.find_elements(By.CSS_SELECTOR, '.c-review-block__room-info-row')
    if len(room_info) > 0:
        room_info = review_selenium_object.find_elements(By.CSS_SELECTOR, '.c-review-block__room-info-row')[0]
        room_type = room_info.find_elements(By.CSS_SELECTOR, '.bui-list__item')[0].text
        room_type_id = room_info.get_attribute("data-room-id")

    stay_details = review_selenium_object.find_elements(By.CSS_SELECTOR, 'ul.c-review-block__stay-date')[0]
    stay_data = stay_details.find_elements(By.CSS_SELECTOR, "div.bui-list__body")[0].text
    stay_data = stay_data.split('·')
    number_of_nights = stay_data[0].split(' ')[0]
    number_of_nights = int(number_of_nights.strip())
    stay_month_year = stay_data[1].strip()
    stay_month_year = datetime.strptime(stay_month_year, '%B %Y').replace(day=1)
    stay_month_year = stay_month_year.strftime('%Y-%m-%d')

    traveller_type_info = review_selenium_object.find_elements(By.CSS_SELECTOR, 'ul.review-panel-wide__traveller_type')
    traveller_type = None
    if len(traveller_type_info) > 0:
        traveller_type_info = traveller_type_info[0]
        traveller_type_element = traveller_type_info.find_elements(By.CSS_SELECTOR, 'div.bui-list__body')
        if len(traveller_type_element) > 0:
            traveller_type = traveller_type_element[0].text

    review_right_side_block = review_selenium_object.find_elements(By.CSS_SELECTOR, "div.c-review-block__right")[0]
    reviewers_choice = review_right_side_block.find_elements(By.CSS_SELECTOR, "span.c-review-block__badge__icon")
    if len(reviewers_choice) > 0:
        reviewers_choice = True
    else:
        reviewers_choice = False

    review_title = None
    review_title_element = review_right_side_block.find_elements(By.CSS_SELECTOR, ".c-review-block__title")
    if len(review_title_element) > 0:
        review_title = review_title_element[0].text

    review_date = None
    review_date_element = review_right_side_block.find_elements(By.CSS_SELECTOR, ".c-review-block__date")
    if len(review_date_element) > 0:
        review_date = review_date_element[0].text
        review_date = review_date.split(':')[1].strip()
        review_date = datetime.strptime(review_date, '%B %d, %Y')
        review_date = review_date.strftime('%Y-%m-%d')

    rating = None
    rating_element = review_right_side_block.find_elements(By.CSS_SELECTOR, ".bui-review-score__badge")
    if len(rating_element) > 0:
        rating = float(rating_element[0].text)

    reviews_pro_and_con = review_selenium_object.find_elements(By.CSS_SELECTOR, ".c-review__row")
    review_pro_text = None
    review_con_text = None
    # reviews_pro_and_con will contain a list of all elements inside this element
    # It can have upto 4 things:
    # 1) pro review which has a green simley face 2) con review which has nothing
    # 3) an option to show translation, 4) 'There are no comments available for this review'
    # through all and retrieve just pro and con if they exist
    for review_row in reviews_pro_and_con:
        smiley = review_row.find_elements(By.CSS_SELECTOR, ".c-review__prefix--color-green")
        if len(smiley) > 0:
            review_pro_text = review_row.find_elements(By.CSS_SELECTOR, ".c-review__body")[0].text
        else:
            if review_row.text != 'Show translation':
                review_con_text = review_row.find_elements(By.CSS_SELECTOR, ".c-review__body")[0].text
                # Handle the case when there are no comments for this review
                if review_con_text == 'There are no comments available for this review':
                    review_con_text = None

    helpful = None
    helpful_info = review_selenium_object.find_elements(By.CSS_SELECTOR, ".review-helpful__vote-others-helpful")
    if len(helpful_info) > 0:
        helpful_info = helpful_info[0]
        if helpful_info.text and len(helpful_info.text) > 0:
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
            image = image.find_elements(By.CSS_SELECTOR, '.c-review-block__photos__button')[0]
            image_src = image.get_attribute('data-photos-src')
            photos_links.append(image_src)
    if photos_links and len(photos_links) > 0:
        photos_links = json.dumps(photos_links)

    # add data to dict
    review_info["review_id"] = review_id
    review_info["reviewer_name"] = reviewer_name
    review_info["country_name"] = country_name
    review_info["type_of_room"] = room_type
    review_info["type_of_room_id"] = room_type_id
    review_info["number_of_nights"] = number_of_nights
    review_info["stay_month_and_year"] = stay_month_year
    review_info["traveller_type"] = traveller_type
    review_info["review_date"] = review_date
    review_info["review_title"] = review_title
    review_info["rating"] = rating
    review_info["reviewers_choice"] = reviewers_choice
    review_info["pros"] = review_pro_text
    review_info["cons"] = review_con_text
    review_info["hotel_owner_response"] = owner_response
    review_info["number_of_people_found_helpful"] = helpful
    review_info["num_photos"] = number_of_photos
    review_info["photos_links"] = photos_links

    return review_info


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

        time.sleep(3)

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
                print('SQL connection failed')
                print(e)
            finally:
                driver.close()
                return

        # Get all the reviews from the first page. Then move to the bottom and move to the 2nd page if it exists
        ALL_REVIEWS = []
        driver.set_window_size(width=1200, height=831)
        time.sleep(2)

        first_page_reviews = driver.find_elements(By.CSS_SELECTOR, 'li.review_list_new_item_block')
        # press continue reading for all owner replies in a page
        continue_reading_button = driver.find_elements(By.CSS_SELECTOR,'a[data-component="ugcs/dom-utils/toggle prevent-default-helper"]')
        for button in continue_reading_button:
            button.click()

        # get all reviews on page1
        for review in first_page_reviews:
            ALL_REVIEWS.append(get_review_data(review, hotel[0]))

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
            # add all reviews of this page to ALL_REVIEWS
            reviews_on_this_page = driver.find_elements(By.CSS_SELECTOR, 'li.review_list_new_item_block')
            for review in reviews_on_this_page:
                ALL_REVIEWS.append(get_review_data(review, hotel[0]))

            next_page_button = driver.find_elements(By.CSS_SELECTOR, 'a.pagenext')
            num_pages += 1
            print(f'        On page number -> {num_pages}')
        print(f'    Number of pages -> {num_pages}')

        # Write all reviews for this hotel into the DB
        for review_data in ALL_REVIEWS:
            try:
                con = get_connector()
                print(f'Entering review id => {review_data["review_id"]}')
                con.enter_booking_review_info(review_data)
                con.close()
            except Exception as e:
                print('SQL connection failed')
                print(e)

        # if all reviews of this business have been added, mark it as complete
        try:
            con = get_connector()
            con.mark_booking_hotel_reviews_complete(hotel[0])
            con.close()
        except Exception as e:
            print('SQL connection failed')
            print(e)
            driver.close()
            return

    except Exception as e:
        print('=================================================================')
        print(f'Got stuck on hotel => {hotel[0]}')
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
            hotels = con.get_booking_hotels_urls_for_reviews()
            print("Number of Hotels: " + str(len(hotels)))
        except Exception as e:
            print("Initialization failed")
            print(e)
            return
        finally:
            con.close()
        for h in hotels:
            queue.put(h)
        queue.join()
    except Exception as e:
        print("Error while running parallel threads")
        traceback.print_exc()

if __name__ == '__main__':
    fetch_hotel_pages()
    print('\a')
