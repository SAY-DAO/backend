from collections import namedtuple
from typing import NamedTuple


class Patterns(NamedTuple):
    url: str
    cost: str
    discontinued: str
    unavaliable: str
    product_status: str
    title: str
    img: str


stores = {
    'digikala': Patterns(
        url='digikala.com',
        cost=r's-rrp-price ">(.*?)<|js-price-value">(.*?)<',
        discontinued='c-product__stock-status--stop-production',
        unavaliable=r'c-product-not-available__title',
        product_status=r'c-product-stock__body">(.*?)<',
        title=r'c-product__title\">(.*?)<',
        img=r's-gallery-img" data-src="(.*?)"',
    ),
    'hodhod': Patterns(
        url='hodhod.com',
        cost=r'<p class="price"><span class="woocommerce-Price-amount amount"><bdi>(.*?)0&()',
        discontinued='c-product__stock-status--stop-production',
        unavaliable=r'stock out-of-stock',
        product_status=r'c-product-stock__body">(.*?)<',
        title=r'product_title entry-title\">(.*?)<',
        img=r'woocommerce-product-gallery__image"><a href="(.*?)"',
    ),
}


def get_patterns(url: str):
    for store in stores.values():
        if store.url in url:
            return store
