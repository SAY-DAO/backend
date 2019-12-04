import re
import requests
from ..api import cache


cost_pattern = r's-rrp-price ">(.*?)<|js-price-value">(.*?)<'
title_pattern = r'c-product__title\">(.*?)<'
img_pattern = r's-gallery-img" data-src="(.*?)"'


def parse_cost(c):
    cost = None
    try:
        cost_text = re.search(
            cost_pattern,
            c,
            re.DOTALL
        ).group(1,2)
        cost_text = cost_text[0] if cost_text[0] else cost_text[1]
        cost_text = cost_text.strip().replace(',', '')
    except:
        # TODO: email to coordinator
        return None

    cost = int(cost_text)
    return cost


def parse_title(c):
    title = None
    try:
        title = re.search(
            title_pattern,
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
            img_pattern,
            c,
            re.DOTALL
        ).group(1).strip()
    except IndexError:
        pass

    return img


#@cache.memoize(timeout=12 * 3600)
def get_data(url):
    try:
       c = requests.get(url).text
    except:
        raise

    cost = parse_cost(c)
    title = parse_title(c)
    img = parse_img(c)

    return dict(cost=cost, img=img, title=title)

