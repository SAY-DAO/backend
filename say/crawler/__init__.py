import functools
import html
import re

import requests
from cachetools import TTLCache
from cachetools import cached

from say.config import configs
from say.crawler.patterns import get_patterns


@cached(
    cache=TTLCache(
        ttl=configs.REQUEST_CACHE_TTL,
        maxsize=configs.REQUEST_CACHE_MAX_SIZE,
    )
)
def request_with_cache(*args, **kwargs):
    return requests.get(*args, **kwargs)


class Crawler:
    def __init__(self, url):
        self.url = url
        self.patterns = get_patterns(self.url)

    def parse_cost(self):
        if self.patterns is None:
            return

        if re.search(
            self.patterns.unavaliable,
            self.c,
            re.DOTALL,
        ):
            return 'unavailable'

        elif raw_cost_text := re.search(self.patterns.cost, self.c, re.DOTALL):
            cost_text = raw_cost_text.group(1, 2)
            cost_text = cost_text[0] if cost_text[0] else cost_text[1]
            cost_text = cost_text.strip().replace(',', '')
            return int(cost_text)

        elif has_product_status := re.search(
            self.patterns.product_status,
            self.c,
            re.DOTALL,
        ):
            product_status = has_product_status.group(1).strip()
            return product_status

        elif re.search(
            self.patterns.unavaliable,
            self.c,
            re.DOTALL,
        ):
            return 'unavailable'

        else:
            return None

    def parse_title(self):
        if self.patterns is None:
            return

        title = None
        try:
            title = re.search(self.patterns.title, self.c, re.DOTALL).group(1).strip()
        except (IndexError, AttributeError):
            pass

        return title

    def parse_img(self):
        if self.patterns is None:
            return

        img = None
        try:
            img = re.search(self.patterns.img, self.c, re.DOTALL).group(1).strip()
        except (IndexError, AttributeError):
            pass

        return img

    def get_data(self, force=False):
        if self.patterns is None:
            return

        if force:
            r = requests.get(self.url)
        else:
            r = request_with_cache(self.url)

        text = r.text
        text = html.unescape(text)
        self.c = text

        cost = self.parse_cost()
        title = self.parse_title()
        img = self.parse_img()
        return dict(cost=cost, img=img, title=title)
