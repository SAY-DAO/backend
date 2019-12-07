import re
import requests
from ..api import cache
from say.tasks import send_email


COST_PATTERN = r's-rrp-price ">(.*?)<|js-price-value">(.*?)<'
DISCONTINUED_PATTERN = 'c-product__stock-status--stop-production'
UNAVALIABLE_PATTERN = 'c-product__stock-status--out-of-stock'
PRODUCT_STATUS_PATTERN = r'c-product-stock__body">(.*?)<'

TITLE_PATTERN = r'c-product__title\">(.*?)<'
IMG_PATTERN = r's-gallery-img" data-src="(.*?)"'
DKP_PATTERN = r'(dkp-\d+)'


def parse_dkp(url):
    return re.search(DKP_PATTERN, url).group(1)


def parse_cost(c):
    cost = None
    try:
        cost_text = re.search(
            COST_PATTERN,
            c,
            re.DOTALL
        ).group(1,2)
        cost_text = cost_text[0] if cost_text[0] else cost_text[1]
        cost_text = cost_text.strip().replace(',', '')
    except:
        has_product_status = re.search(
            r'c-product-stock__body">(.*?)<',
            c,
            re.DOTALL,
        )
        if not has_product_status:
            raise

        product_status = has_product_status.group(1).strip()
        return product_status

    cost = int(cost_text)
    return cost


def parse_title(c):
    title = None
    try:
        title = re.search(
            TITLE_PATTERN,
            c,
            re.DOTALL
        ).group(1).strip()
    except IndexError:
        pass

    return title


def parse_img(c):
    img = None
    try:
        img = re.search(
            IMG_PATTERN,
            c,
            re.DOTALL
        ).group(1).strip()
    except IndexError:
        pass

    return img


#@cache.memoize(timeout=12 * 3600)
def get_data(url):
    dkp = parse_dkp(url)
    try:
       c = requests.get(url).text
    except:
        raise

    cost = parse_cost(c)
    title = parse_title(c)
    img = parse_img(c)

    return dict(dkp=dkp, cost=cost, img=img, title=title)

