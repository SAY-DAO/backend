import re
import requests
from bs4 import BeautifulSoup
from ..api import cache


price_pattern = r'''c-product__seller-price-raw js-price-value">(.*?)<|c-product__seller-price-prev js-rrp-price">(.*?)<'''
#TODO namojood

#@cache.memoize(timeout=12 * 3600)
def get_data(url):
    price = None
    try:
       c = requests.get(url).text
    except:
        raise

    try:
        price_text = re.search(
            price_pattern,
            c,
            re.DOTALL
        ).group(1).strip().replace(',', '')
    except IndexError:
        raise

    price = int(price_text)
    return dict(price=price)
