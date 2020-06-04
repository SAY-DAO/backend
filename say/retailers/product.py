class RetailerProduct(object):

    def __init__(self, data):
        self.data = data

    @property
    def title(self):
        raise NotImplementedError()

    @property
    def img(self):
        raise NotImplementedError()

    @property
    def cost(self):
        raise NotImplementedError()

    @property
    def status(self):
        raise NotImplementedError()


