import functools
import html
import re
from typing import NamedTuple
import urllib.request
import json
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


class DigikalaCrawler:
    API_URL_NOT_FRESH = 'https://api.digikala.com/v2/product/%s/'
    API_URL_FRESH = 'https://api-fresh.digikala.com/v1/product/%s/'
    DKP_PATTERN = re.compile(r'.*/dkp-(\d+).*')

    def __init__(self, url):
        try:
            self.dkp = self.DKP_PATTERN.findall(string=url)[0]
        except IndexError:
            self.dkp = None


    def call_api(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                status_code = response.getcode()
                content = response.read().decode('utf-8')
                return status_code, content
        except urllib.error.URLError as e:
            return None, f"An error occurred: {e}"

    def parse_result(self, api_response):
        try:
            # Parse the JSON response
            json_response = json.loads(api_response[1])
            return json_response
        except json.JSONDecodeError as e:
            return f"An error occurred while parsing JSON: {e}"

    def get_data(self, force):
        result = None
        parsed_result = None

        if self.dkp is None:
            return

        url = self.API_URL_NOT_FRESH % self.dkp
        print("url:")
        print(url)
        api_response = self.call_api(url)
        parsed_result = self.parse_result(api_response)

        print(parsed_result)
        if int(parsed_result["status"]) == 200:
            parsed_result = self.parse_result(api_response)
        elif parsed_result["status"] == 302 and "fresh" in parsed_result["redirect_url"]["uri"]:
            url = self.API_URL_FRESH % self.dkp
            api_response = self.call_api(url)
            parsed_result = self.parse_result(api_response)
            if parsed_result["status"] != 200:
                print("Could not update!")
                return
            else:
                parsed_result = self.parse_result(api_response)

        else:
            print("Could not update!")
            print(url)
            return

        result = parsed_result["data"]


        if result['product'].get('is_inactive'):
            return dict(cost='unavailable', img=None, title=None)

        title = result['product']['title_fa']
        if result['product']['status'] == 'marketable':
            cost = int(result['product']['default_variant']['price']['rrp_price']) // 10
        else:
            cost = 'unavailable'

        img = result['product']['images']['main']['url'][0]
        return dict(cost=cost, img=img, title=title)



