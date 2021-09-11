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
        cost=r'<meta property="product:price:amount" content="(\d+)">()',
        discontinued='c-product__stock-status--stop-production',
        unavaliable=r'stock out-of-stock',
        product_status=r'c-product-stock__body">(.*?)<',
        title=r'<meta property="og:image:alt" content="([^"]+)">',
        img=r'<meta property="og:image:secure_url" content="([^"]+)">',
    ),
}


def get_patterns(url: str):
    for store in stores.values():
        if store.url in url:
            return store
