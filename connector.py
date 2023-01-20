import mysql.connector
from mysql.connector import Error
import yaml
import argparse
from datetime import datetime, timedelta
from logger import logger


class Connector():

    DB_SERVER = None
    USER_NAME = None
    USER_PASSWORD = None
    DB_NAME = None

    connection = None

    def __init__(self):
        with open("conf.yaml", 'r') as stream:
            yaml_loader = yaml.safe_load(stream)
            DB_SERVER = yaml_loader.get('db_server')
            USER_NAME = yaml_loader.get('user_name')
            USER_PASSWORD = yaml_loader.get('user_password')
            DB_NAME = yaml_loader.get('db_name')
        self.connection = self.create_connection(DB_SERVER, USER_NAME, USER_PASSWORD, DB_NAME)

    def create_connection(self, host_name, user_name, user_password, db_name):
        try:
            self.connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name,
                port=3306
            )
            logger.info("Connection to MySQL DB successful")
        except Error as e:
            logger.error("The error " + str(e) + " occurred")
            logger.exception("Exception: ")
        return self.connection

    def close(self):
        self.connection.close()

    def clean_db(self, run_date, location):
        logger.info('Cleaning')

        cursor = self.connection.cursor()
        # cursor.execute('DELETE FROM expedia_hotels')
        # cursor.execute('DELETE FROM expedia_photos')
        # cursor.execute('DELETE FROM expedia_hotel_rankings where search_start_date = %s and location = %s', [run_date, location])
        # cursor.execute('DELETE FROM booking_hotels')
        # cursor.execute('DELETE FROM booking_photos')
        # cursor.execute('DELETE FROM booking_hotel_rankings where run_date = %s', [run_date])
        self.connection.commit()

    def get_booking_locations(self):
        sql = "SELECT destination, dest_id, dest_type, iata from booking_locations where iata not in ('NYCwef')"

        cursor = self.connection.cursor()
        cursor.execute(sql, [])

        locations = cursor.fetchall()
        return locations

    def get_booking_location(self, iata):
        sql = "SELECT destination from booking_locations where iata = %s"

        cursor = self.connection.cursor()
        cursor.execute(sql, [iata])

        locations = cursor.fetchall()
        return locations

    def enter_booking_hotel_photos(self, hotel_id, photo_src):
        sql = 'INSERT INTO booking_photos ( hotel_id, image_src ) SELECT %s, %s as tmp'

        val = [
            hotel_id, photo_src
        ]

        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def enter_booking_hotel_ranking(self, listing, rank, search_start_date, search_end_date, location, today):
        sql = 'INSERT INTO booking_hotel_rankings ( run_date, search_start_date, search_end_date, rank, hotel_id, location, '\
            ' location_addon, discounted_price, original_price, rating, comment, review_count, sponsored, badges, '\
            ' recommended_unit, recommended_unit_beds, availability, occupancy, external_rating, external_comment, external_review_count) '\
            ' SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s as tmp '

        val = [
            today, search_start_date, search_end_date, rank, listing['hotel_id'], location,
            listing['location_addon'], listing['discounted_price'], listing['original_price'], listing['rating'], listing['comment'],
            listing['review_count'], listing['sponsored'], str(listing['badges']),
            listing['recommended_unit'], listing['recommended_unit_beds'], listing['availability'], listing['occupancy'],
            listing['external_rating'], listing['external_comment'],
            listing['external_review_count'],
        ]

        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def enter_booking_hotel(self, listing, location):
        sql = 'INSERT INTO booking_hotels ( hotel_id, name, locality, location, '\
            ' rating, comment, review_count, url, map_url, review_fetched, badges, '\
            ' distance_from_center, location_addon) '\
            ' SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s as tmp'

        val = [
            listing['hotel_id'], listing['name'], listing['locality'],
            location, listing['rating'], listing['comment'], listing['review_count'],
            listing['url'], listing['map_url'], 0, str(listing['badges']),
            listing['distance_from_center'], listing['location_addon']
        ]
        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def shift_booking_rankings(self, loc, run_date, start_date):
        sql = 'UPDATE booking_hotel_rankings set run_date=%s'\
            ' WHERE location = %s and run_Date = %s and search_start_date = %s'

        val = [
             run_date + timedelta(days=1), loc, run_date, start_date
        ]
        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def clean_booking_rankings(self, loc, run_date, start_date):
        sql = 'DELETE from booking_hotel_rankings '\
            ' WHERE location = %s and run_Date = %s and search_start_date = %s'

        val = [
            loc, run_date, start_date
        ]
        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def update_booking_hotel(self, listing):
        sql = 'UPDATE booking_hotels set rating=%s, comment=%s, review_count=%s, badges=%s '\
            ' WHERE hotel_id = %s'

        val = [
            listing['rating'], listing['comment'], listing['review_count'],
            str(listing['badges']),
            listing['hotel_id']
        ]
        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def get_booking_hotel(self, name, location, locality):
        sql = "SELECT hotel_id FROM booking_hotels where name = %s and location = %s and locality = %s"

        cursor = self.connection.cursor()
        cursor.execute(sql, [name, location, locality])

        hotels = cursor.fetchall()
        if len(hotels) == 1:
            return hotels[0][0]
        return None

    def does_booking_hotel_exist(self, hotel_id):
        sql = "SELECT 1 FROM booking_hotels where hotel_id = %s"

        val = [hotel_id]
        cursor = self.connection.cursor()
        cursor.execute(sql, val)

        hotels = cursor.fetchall()
        if len(hotels) == 1:
            return True
        return False

    def enter_expedia_hotel_photos(self, hotel_id, photos):
        sql = 'INSERT INTO expedia_photos ( hotel_id, image_src ) SELECT %s, %s as tmp'

        for photo_src in photos:
            val = [
                hotel_id, photo_src
            ]

            self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def enter_expedia_hotel_ranking(self, listing, rank, search_start_date, search_end_date, location, today):
        sql = 'INSERT INTO expedia_hotel_rankings ( run_date, search_start_date, search_end_date, rank, hotel_id, location, '\
            ' price, original_price, total_price, rating, comment, review_count, review_text, sponsored, amenities, badges, '\
            ' full_text, access) SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s as tmp '

        val = [
            today, search_start_date, search_end_date, rank, listing['hotel_id'], location,
            listing['price'], listing['original_price'], listing['total_price'], listing['rating'], listing['comment'],
            listing['review_count'], listing['full_review'], listing['sponsored'], str(listing['amenities']),
            str(listing['badges']), listing['full_text'], listing['vip_access']
        ]

        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def enter_expedia_hotel(self, listing, location):
        sql = 'INSERT INTO expedia_hotels ( hotel_id, name, access, locality, location, '\
            ' rating, comment, review_count, url, review_text, conflict, review_fetched, amenities, badges ) '\
            ' SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s as tmp'

        val = [
            listing['hotel_id'], listing['name'], listing['vip_access'], listing['nbh'],
            location, listing['rating'], listing['comment'], listing['review_count'],
            listing['url'], listing['full_review'], listing['conflict'], 0,
            str(listing['amenities']), str(listing['badges'])
        ]
        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def update_expedia_hotel(self, listing):
        sql = 'UPDATE expedia_hotels set access=%s, rating=%s, comment=%s, review_count=%s, review_text=%s, conflict=%s, amenities=%s, badges=%s '\
            ' WHERE hotel_id = %s'

        val = [
            listing['vip_access'], listing['rating'], listing['comment'], listing['review_count'],
            listing['full_review'], listing['conflict'], str(listing['amenities']), str(listing['badges']),
            listing['hotel_id']
        ]
        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def get_expedia_locations(self):
        sql = "SELECT destination, region_id FROM expedia_locations where iata not in ('LAghfd X')"

        cursor = self.connection.cursor()
        cursor.execute(sql, [])

        locations = cursor.fetchall()
        return locations

    def get_expedia_hotel(self, name, location, locality):
        sql = "SELECT hotel_id FROM expedia_hotels where name = %s and location = %s and locality = %s"

        cursor = self.connection.cursor()
        cursor.execute(sql, [name, location, locality])

        hotels = cursor.fetchall()
        if len(hotels) == 1:
            return hotels[0][0]
        return None

    def does_expedia_hotel_exist(self, hotel_id):
        sql = "SELECT 1 FROM expedia_hotels where hotel_id = %s"

        val = [hotel_id]
        cursor = self.connection.cursor()
        cursor.execute(sql, val)

        hotels = cursor.fetchall()
        if len(hotels) == 1:
            return True
        return False

    def get_expedia_hotel_urls(self):
        sql = "SELECT hotel_id, url FROM expedia_hotels where url is not Null and flag is NULL  order by url"

        cursor = self.connection.cursor()
        cursor.execute(sql, [])

        hotels = cursor.fetchall()
        return hotels

    def get_expedia_hotel_review_ids(self, hotel_id):
        sql = "select review_id from `expedia_hotels_reviews_info` where hotel_id = %s"

        cursor = self.connection.cursor()
        cursor.execute(sql, [hotel_id])

        ids = [a[0] for a in cursor.fetchall()]
        return set(ids)

    def enter_expedia_hotel_info(self, hotel_info):
        sql = 'INSERT INTO expedia_hotels_info ( hotel_id,latitude,locality,longitude,postal_code,region,street_address,title, country) '\
            ' SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s as tmp'

        val = [
            hotel_info['hotel_id'], hotel_info['latitude'], hotel_info['locality'], hotel_info['longitude'],
            hotel_info['postal_code'], hotel_info['region'], hotel_info['street_add'],
            hotel_info['title'], hotel_info['country']
        ]
        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def enter_expedia_review_info(self, review_info):
        sql = 'INSERT INTO expedia_hotels_reviews_info (  '\
            ' brandType, title,  negative_feedback, positive_feedback, response_responder, date_responder, name_responder,'\
            ' review_text, photos, photos_count, rating, user_name, review_date, likes_count, review_id, rating_comment, hotel_id '\
            ' ) SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s as tmp'

        val = [
            'EXPEDIA', review_info['title'], review_info['disliked'], review_info['liked'], 
            review_info['owner_response'], review_info['owner_response_date'], 
            review_info['owner'], review_info['review_text'], review_info['photos'], 
            review_info['photos_count'], int(review_info['rating'].split('/')[0]), review_info['user'], 
            review_info['date'], review_info['like_count'], review_info['review_id'],
            review_info['rating'].split(' ')[1], review_info['hotel_id']
        ]
        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def mark_hotel_compplete(self, hotel_id):
        sql = 'UPDATE expedia_hotels set flag = 1 where hotel_id = %s '

        val = [
            hotel_id
        ]
        print(hotel_id)
        self.connection.cursor().execute(sql, val)
        self.connection.commit()


    def mark_hotel_incompplete(self, hotel_id):
        sql = 'UPDATE expedia_hotels set flag = 2 where hotel_id = %s '

        val = [
            hotel_id
        ]
        print(hotel_id)
        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def dummy(self):
        sql = 'insert into `expedia_hotels`(hotel_id, name) values(%s, %s)'

        val = [
            '123123123', 'NEW🌟Spaciou'
        ]
        self.connection.cursor().execute(sql, val)
        self.connection.commit()


def get_connector():
    return Connector()


connector = Connector()

if __name__ == '__main__':
    # connector.dummy()
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean-db', dest='delete',
                        default=False, action="store_true",
                        help='Delete the db entrie')
    parser.add_argument('--date', dest='run_date',
                        help='Delete the db entrie')

    parser.add_argument('--location', dest='location',
                        help='Delete the db entrie')
    input_values = parser.parse_args()

    if input_values.delete and input_values.run_date:
        dt = datetime.strptime(input_values.run_date, "%Y-%m-%d")
        # connector.clean_db(dt, input_values.location)
        print("Be extremely careful with the below query.")
