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
        self.connection.commit()

    def enter_expedia_hotel_photos(self, hotel_id, photos):
        sql = 'INSERT INTO expedia_photos ( hotel_id, image_src ) SELECT %s, %s as tmp'

        for photo_src in photos:
            val = [
                hotel_id, photo_src
            ]

            self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def enter_expedia_hotel_ranking(self, hotel_id, rank, search_start_date, search_end_date, location):
        sql = 'INSERT INTO expedia_hotel_rankings ( run_date, search_start_date, search_end_date, rank, hotel_id, location) SELECT %s, %s, %s, %s, %s, %s as tmp '

        val = [
            datetime.date.today(), search_start_date, search_end_date, rank, hotel_id, location
        ]

        self.connection.cursor().execute(sql, val)
        self.connection.commit()

    def enter_expedia_hotel(self, listing):
        sql = 'INSERT INTO expedia_hotels ( hotel_id, name, access, locality, location, rating, comment, review_count, original_price, price, total_price, url, full_text, review_text ) '\
            ' SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s as tmp'

        val = [
            listing['hotel_id'], listing['name'], listing['vip_access'], listing['nbh'], listing['loc'], listing['rating'], listing['comment'], listing['review_count'], listing['original_price'], listing['price'], listing['total_price'], listing['url'], listing['full_text'], listing['full_review']
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
        sql = "SELECT 1 FROM expedia_hotels where hotel_id = %"

        cursor = self.connection.cursor()
        cursor.execute(sql, [hotel_id])

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
