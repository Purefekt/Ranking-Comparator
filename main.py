import datetime

from requester import *
from expedia_scrapper import fetch_rankings as ex_fetch_rankings
from booking_scrapper import fetch_rankings as bk_fetch_rankings

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import urlencode


connector = None


def main():
    # send_raw_file("A", 'RUNDATE_' + str(datetime.date.today()) + '/', 'page.html.gz')
    # return
    # parser = argparse.ArgumentParser()

    # parser.add_argument('-b', '--businesses', dest='businesses', default=False,
    #                     action="store_true", help='Fetch businesses (Default:False)')

    # input_values = parser.parse_args()

    try:
        today = datetime.date.today()
        logger.info("RUNDATE- " + str(today))
        # ex_fetch_rankings(today + datetime.timedelta(days=1), today + datetime.timedelta(days=2))
        # bk_fetch_rankings(today + datetime.timedelta(days=1), today + datetime.timedelta(days=2))
        # return

        for i in range(0, 30):
            print()
            print()
            print()
            print()
            print()
            print()
            print("-----------------------------")
            print("-----------------------------")
            print("DATE CHANGE")
            print(str(today) + "   " + str(datetime.timedelta(days=i)))
            logger.info("DATE: " + str(today) + "   " + str(datetime.timedelta(days=i)))
            print()
            print("-----------------------------")
            print("-----------------------------")
            print("EXPEDIA")
            logger.info("EXPEDIA")
            ex_fetch_rankings(today + datetime.timedelta(days=i), today + datetime.timedelta(days=i + 1), today)
            print()
            print("-----------------------------")
            print("-----------------------------")
            print("BOOKING")
            logger.info("BOOKING")
            bk_fetch_rankings(today + datetime.timedelta(days=i), today + datetime.timedelta(days=i + 1), today)

    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )


if __name__ == '__main__':
    main()
