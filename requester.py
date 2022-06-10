import requests
import yaml
import time
import random
from logger import logger

# from logger import logger

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    from urllib.parse import quote
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib import quote

with open("conf.yaml", 'r') as stream:
    content = yaml.safe_load(stream)
    SP_USER = content.get('smart_proxy_user')
    SP_PWD = content.get('smart_proxy_password')
proxy_url = "http://" + SP_USER + ":" + SP_PWD + "@149.28.81.160:20000"


def generic_request(host, path, url_params=None, with_token=False, with_proxy=True):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    headers = {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    if with_token:
        headers['Authorization'] = 'Bearer %s' % get_random_api_key()

    logger.info(u'Querying {0} ...'.format(url))
    logger.info("Params: " + str(url_params))

    i = 0
    while i < 10:
        try:

            if with_proxy:
                # # Zyte IP Proxy
                # response = requests.request('GET', url, headers=headers, params=url_params,
                #                             proxies={
                #                                 "http": "http://" + ZYTE_API_KEY + ":@proxy.crawlera.com:8011/",
                #                                 "https": "http://" + ZYTE_API_KEY + ":@proxy.crawlera.com:8011/",
                #                             },
                #                             verify='./zyte-proxy-ca.crt'
                #                             )

                # # Smart Proxy
                response = requests.request('GET', url, headers=headers, params=url_params,
                                            proxies={
                                                "http": proxy_url,
                                                "https": proxy_url,
                                            }
                                            )
            else:
                response = requests.request('GET', url, headers=headers, params=url_params)

            if response.status_code != 200:
                if i == 9:
                    logger.error("Request failed " + str(response.status_code))
                    print("Request failed " + str(response.status_code))
                    raise Exception("Unable to fetch data from url " + url)
            else:
                logger.info("Request successful")
                print("Returning")
                return response
        except Exception as e:
            if i == 9:
                logger.exception("ERROR: ")
                print("Error: " + str(e))
                raise
        i = i + 1
        # logger.info("Retrying")
        # time.sleep(0.2)


def request_json(host, path, url_params=None, with_token=False, with_proxy=False):
    return generic_request(host, path, url_params, with_token, with_proxy).json()


def get_random_api_key():
    return ACCESS_TOKEN[random.randint(0, len(ACCESS_TOKEN) - 1)]['api_key']
