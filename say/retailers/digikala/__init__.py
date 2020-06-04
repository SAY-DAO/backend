import re
import requests
from ..api import cache
from .product import DigikalaProduct
from ..retailer import Retailer


class DigikalaRetailer(Retailer):

    DKP_PATTERN = r'(dkp-\d+)'

    def _parse_dkp(self, url):
        return re.search(DKP_PATTERN, url).group(1)

    @cache.memoize(timeout=1 * 3600)
    def get_product(self, url):
        dkp = parse_dkp(url)
        c = requests.get(url).text
        return DigikalaProduct(c)

