import re

from say.stauses import ProductStatus
from ..product import RetailerProduct


class DigikalaProduct(RetailerProduct):

    COST_PATTERN = r's-rrp-price ">(.*?)<|js-price-value">(.*?)<'
    TITLE_PATTERN = r'c-product__title\">(.*?)<'
    IMG_PATTERN = r's-gallery-img" data-src="(.*?)"'

    DISCONTINUED_PATTERN = 'c-product__stock-status--stop-production'
    UNAVALIABLE_PATTERN = 'c-product__stock-status--out-of-stock'
    AVALIABLE_PATTERN = 'btn-add-to-cart--full-width'


    def _parser(self, pattern):
        return re.search(pattern, self.data, re.DOTALL)

    @property
    def title(self):
        return self._parser(self.TITLE_PATTERN).group(1).strip()

    @property
    def img(self):
        return self._parser(self.IMG_PATTERN).group(1).strip()

    @property
    def cost(self):
        try:
            cost = self._parser(COST_PATTERN).group(1,2)
            cost = cost[0] or cost[1]
            cost = cost.strip().replace(',', '')
            return cost
        except:
            return None

    @property
    def status(self):
        if self._parser(self.AVALIABLE_PATTERN):
            return ProductStatus.avaliable

        elif self._parser(self.UNAVALIABLE_PATTERN):
            return ProductStatus.unavaliable)

        elif self._parser(self.DISCONTINUED_PATTERN):
            return ProductStatus.discontinued

        else:
            raise Exception('Unknown Product Status')

