class Handler(object):
    """
    Abstract class for handler classes that are outputs for the created events.
    """
    def handle(self, item):
        """
        Handle the given event here, the item is a dict containing id, timestamp 
        and value
        """
        raise NotImplementedError

    def close(self, item):
        raise NotImplementedError
