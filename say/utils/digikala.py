import re

import requests


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
    if raw_cost_text := re.search(
        COST_PATTERN,
        c,
        re.DOTALL
    ):
        cost_text = raw_cost_text.group(1, 2)
        cost_text = cost_text[0] if cost_text[0] else cost_text[1]
        cost_text = cost_text.strip().replace(',', '')
        return int(cost_text)

    elif has_product_status := re.search(
        r'c-product-stock__body">(.*?)<',
        c,
        re.DOTALL,
    ):
        product_status = has_product_status.group(1).strip()
        return product_status
    
    elif product_unavailable := re.search(
        r'c-product-not-available__title',
        c,
        re.DOTALL,
    ):
        return 'unavailable'
    
    else:
        return None


def parse_title(c):
    title = None
    try:
        title = re.search(
            TITLE_PATTERN,
            c,
            re.DOTALL
        ).group(1).strip()
    except (IndexError, AttributeError):
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
    except (IndexError, AttributeError):
        pass

    return img


def get_data(url):
    dkp = parse_dkp(url)
    c = requests.get(url).text

    cost = parse_cost(c)
    title = parse_title(c)
    img = parse_img(c)

    return dict(dkp=dkp, cost=cost, img=img, title=title)
