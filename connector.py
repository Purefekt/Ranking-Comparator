import mysql.connector
from mysql.connector import Error
import yaml
import argparse
import datetime
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
                database=db_name
            )
            logger.info("Connection to MySQL DB successful")
        except Error as e:
            logger.info("The error " + str(e) + " occurred")
        return self.connection

    def close(self):
        self.connection.close()

    def clean_db(self):
        logger.info('Cleaning')

        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM expedia_hotels')
        cursor.execute('DELETE FROM expedia_photos')
        cursor.execute('DELETE FROM expedia_hotel_rankings')
        cursor.execute('DELETE FROM booking_hotels')
        cursor.execute('DELETE FROM booking_photos')
        cursor.execute('DELETE FROM booking_hotel_rankings')
        self.connection.commit()

    def get_booking_locations(self):
        sql = "select destination, dest_id, dest_type, iata from booking_locations"

        cursor = self.connection.cursor()
        cursor.execute(sql, [])

        locations = cursor.fetchall()
        return locations

    def enter_booking_hotel_photos(self, hotel_id, photo_src):
        sql = 'INSERT INTO booking_photos ( hotel_id, image_src ) SELECT %s, %s as tmp'

        val = [
            hotel_id, photo_src
        ]

        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def enter_booking_hotel_ranking(self, listing, rank, search_start_date, search_end_date, location):
        sql = 'INSERT INTO booking_hotel_rankings ( run_date, search_start_date, search_end_date, rank, hotel_id, location, '\
            ' location_addon, discounted_price, original_price, rating, comment, review_count, sponsored, badges, '\
            ' recommended_unit, recommended_unit_beds, availability, occupancy, external_rating, external_comment, external_review_count) '\
            ' SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s as tmp '

        val = [
            datetime.date.today(), search_start_date, search_end_date, rank, listing['hotel_id'], location,
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

    def enter_expedia_hotel_ranking(self, listing, rank, search_start_date, search_end_date, location):
        sql = 'INSERT INTO expedia_hotel_rankings ( run_date, search_start_date, search_end_date, rank, hotel_id, location, '\
            ' price, original_price, total_price, rating, comment, review_count, review_text, sponsored, amenities, badges, '\
            ' full_text, access) SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s as tmp '

        val = [
            datetime.date.today(), search_start_date, search_end_date, rank, listing['hotel_id'], location,
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
        sql = "SELECT destination, region_id FROM expedia_locations"

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


def get_connector():
    return Connector()


connector = Connector()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean-db', dest='delete',
                        default=False, action="store_true",
                        help='Delete the db entrie')
    input_values = parser.parse_args()

    if input_values.delete:
        connector.clean_db()
        print("Be extremely careful with the below query.")
