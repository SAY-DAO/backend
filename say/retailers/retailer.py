from .product import RetailerProduct


class Retailer(object):

    def get_data(self, url) -> RetailerProduct:
        '''
        Parameters:
            url: url of product

        Returns:
            RetailerProduct
        '''
        raise NotImplementedError()

