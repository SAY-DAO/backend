import requests
from bs4 import BeautifulSoup
from ..api import cache

@cache.memoize(timeout=12 * 3600)
def get_price(url):
    price = None
    try:
       result = requests.get(url)
       soup = BeautifulSoup(result.content, features="html.parser")
       price_div = soup.find("div", "c-product__seller-price-raw js-price-value")
       price_text = price_div.text.strip().replace(',', '')
       price = int(price_text)
    except:
        pass

    return price
