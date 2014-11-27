class Handler(object):
    def handle(self, item):
        raise NotImplementedError

    def close(self, item):
        raise NotImplementedError
